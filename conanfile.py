from conans import ConanFile, AutoToolsBuildEnvironment, CMake, tools
import os

class ApacheaprConan(ConanFile):
    name = "apache-apr"
    version = "1.6.3"
    license = "Apache-2.0"
    url = "https://github.com/malwoden/conan-apache-apr"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    lib_name = name + "-" + version

    def source(self):
        file_ext = ".tar.gz" if not self.settings.os == "Windows" else "-win32-src.zip"
        tools.get("http://archive.apache.org/dist/apr/apr-" + self.version + file_ext)

    def build_windows(self, install_folder):
        build_target = "libapr-1" if self.options.shared else "apr-1"

        cmake = CMake(self)
        cmake.definitions["INSTALL_PDB"] = "OFF"
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = install_folder
        cmake.configure(source_folder="apr-%s" % self.version)
        cmake.build(target=build_target)
        cmake.install()

    def build_linux(self, install_folder):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = self.options.shared
        with tools.environment_append(env_build.vars):
            configure_command = "./configure"
            configure_command += " --prefix=" + install_folder
            configure_command += " --enable-shared=" + ("yes" if self.options.shared else "no")
            configure_command += " --enable-static=" + ("yes" if not self.options.shared else "no")

            src_path_abs = self.source_folder + "/apr-" + self.version

            with tools.chdir(src_path_abs):
                self.run(configure_command)
                self.run("make -j " + str(max(tools.cpu_count() - 1, 1)))
                self.run("make install")

    def build(self):
        install_folder = self.build_folder + "/buildinstall"

        if self.settings.os == "Linux":
            self.build_linux(install_folder)
        else:
            self.build_windows(install_folder)

    def package(self):
        base_path = self.build_folder + "/buildinstall/"

        # libapr-1 is shared, apr-1 is static
        if self.options.shared == True:
            self.copy("*.so*", dst="lib", src=base_path + "lib", keep_path=False)
            self.copy("libapr-1.lib", dst="lib", src=base_path + "lib", keep_path=False)
            self.copy("libapr-1.dll", dst="bin", src=base_path + "bin", keep_path=False)
        else:
            self.copy("apr-1.a", dst="lib", src=base_path + "lib", keep_path=False)
            self.copy("apr-1.lib", dst="lib", src=base_path + "lib", keep_path=False)

        # self.copy("apr-1-config", dst="bin", src="bin", keep_path=False)
        self.copy("*.h", dst="include", src=base_path + "include", keep_path=True)

        # if self.settings.os == "Linux":
        #     self.copy("*.so*", dst="lib", src="lib", keep_path=False)
        #     self.copy("*.a", dst="lib", src="lib", keep_path=False)
        #     self.copy("*.h", dst="include", src="include", keep_path=True)
        #     self.copy("*", dst="build-1", src="build-1", keep_path=True)
        # else:
        #     self.copy("*.dll*", dst="bin", src=self.build_folder + "/package/bin", keep_path=False)
        #     self.copy("*.lib", dst="lib", src=self.build_folder + "/package/lib", keep_path=False)
        #     self.copy("*.h", dst="include", src=self.build_folder + "/package/include", keep_path=True)


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            # self.cpp_info.includedirs = ["include/apr-1"]
            self.cpp_info.libs.append("dl")
            self.cpp_info.cppflags = ["-pthread"]

        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.defines = ["APR_DECLARE_STATIC"]
            else:
                self.cpp_info.defines = ["APR_DECLARE_EXPORT"]

        self.cpp_info.libs.append("Ws2_32")
        self.cpp_info.libs.append("Rpcrt4")

