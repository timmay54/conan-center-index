from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=1.50.0"


class NanoPBConan(ConanFile):
    name = "nanopb"
    description = "Protocol Buffers with small code size"
    topics = ("nanopb", "protobuf")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nanopb/nanopb"
    license = "Zlib"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # BUILD_SHARED_LIBS and POSITION_INDEPENDENT_CODE are automatically parsed when self.options.shared or self.options.fPIC exist
        tc = CMakeToolchain(self)
        # Boolean values are preferred instead of "ON"/"OFF"
        tc.variables["PACKAGE_CUSTOM_DEFINITION"] = True
        if is_msvc(self):
            # don't use self.settings.compiler.runtime
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        # deps_cpp_info, deps_env_info and deps_user_info are no longer used
        if self.dependencies["dependency"].options.foobar:
            tc.variables["DEPENDENCY_LIBPATH"] = self.dependencies["dependency"].cpp_info.libdirs
        # cache_variables should be used sparingly, example setting cmake policies
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        # In case there are dependencies listed on requirements, CMakeDeps should be used
        tc = CMakeDeps(self)
        tc.generate()
        # In case there are dependencies listed on build_requirements, VirtualBuildEnv should be used
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        include_folder = os.path.join(self.source_folder, "include")
        copy(self, "*", src=include_folder, dst=os.path.join(self.package_folder, "include"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nanopb")
        self.cpp_info.set_property("cmake_target_name", "nanopb::nanopb")
        self.cpp_info.set_property("pkg_config_name", "nanopb")
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.libs = ["protobuf-nanopb"]
