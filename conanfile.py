from conans import ConanFile, CMake, MSBuild, AutoToolsBuildEnvironment, tools
import os
import shutil



class ZziplibConan(ConanFile):
    name = "zziplib"
    version = "0.13.69"
    folder_name = "{}-{}".format(name, version)
    license = "LGPL-2"
    author = "konrad.no.tantoo"
    url = "https://github.com/KonradNoTantoo/zziplib_conan"
    exports = "CMakeLists.txt", "config.h.in.cmake"
    description = "The zziplib provides read access to zipped files in a zip-archive, using compression based solely on free algorithms provided by zlib. It also provides a functionality to overlay the archive filesystem with the filesystem of the operating system environment."
    topics = ("zip", "compression", "conan")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"


    def copy_file_to_source(self, name):
        file_content = tools.load(name)
        path_to_source = os.path.join(self.source_folder, self.folder_name, name)
        tools.save(path_to_source, file_content)
        print("Copied", name, "=>", path_to_source)


    def requirements(self):
        self.requires("zlib/1.2.11@conan/stable")


    def config(self):
        del self.settings.compiler.libcxx


    def source(self):
        archive_name = "{}.tar.gz".format(self.folder_name)
        tarball_path = "https://github.com/gdraheim/zziplib/archive/v{}.tar.gz".format(self.version)
        tools.get(tarball_path, filename=archive_name)
        if self.settings.compiler == "Visual Studio" and self.settings.arch != "x86":
            self.copy_file_to_source("CMakeLists.txt")
            self.copy_file_to_source("config.h.in.cmake")
        else:
            tools.replace_in_file(os.path.join(self.folder_name, "Makefile.in"),
                "SUBDIRS = zzip zzipwrap bins test docs", "SUBDIRS = zzip zzipwrap bins test", strict=False)


    def build(self):
        if self.settings.compiler == "Visual Studio":
            if self.settings.arch == "x86":
                # existing .sln works only for x86 builds
                msbuild = MSBuild(self)
                msbuild.build("{}/msvc8/zziplib.sln".format(self.folder_name), platforms={"x86":"Win32"})
            else:
                # install custom CMakeLists in source and use CMake
                cmake = CMake(self)
                if self.options.shared:
                    cmake.definitions["ZZIP_DLL"] = "ON"
                cmake.configure(source_folder=self.folder_name)
                cmake.build()
        else:
            build_target = "zzip{}-build".format(64 if self.settings.arch == "x86_64" else 32)
            with tools.chdir(self.folder_name):
                env_build = AutoToolsBuildEnvironment(self)
                if self.options.shared:
                    env_build.configure(args=["--disable-static"])
                else:
                    env_build.configure(args=["--enable-static"])
                env_build.make()


    def package(self):
        exported_headers = [
            "zzip/conf.h",
            "zzip/types.h",
            "zzip/zzip.h",
            "zzip/plugin.h",
        ]

        if self.settings.compiler == "Visual Studio":
            exported_headers.append("zzip/_msvc.h")

        for header in exported_headers:
            self.copy(header, dst="include", src=self.folder_name, keep_path=True)

        self.copy("zzip/_config.h", dst="include", keep_path=True)

        for name in ["zzip", "zzipfseeko", "zzipmmapped", "zzipwrap"]:
            self.copy("*/{}lib.dll".format(name), dst="bin", keep_path=False)
            self.copy("*/{}lib.lib".format(name), dst="lib", keep_path=False)
            if self.options.shared:
                self.copy("*/lib{}.so".format(name), dst="lib", keep_path=False)
            else:
                self.copy("*/lib{}.a".format(name), dst="lib", keep_path=False)


    def package_info(self):
        self.cpp_info.libs = ["zziplib"]
