from conans import ConanFile, CMake, tools, Meson
import os

class GstvalidateConan(ConanFile):
    name = "gst-validate-1.0"
    version = "1.14.4"
    description = "Development and debugging tools for GStreamer"
    url = "https://github.com/conan-multimedia/gst-validate-1.0"
    homepage = "https://github.com/GStreamer/gst-devtools"
    license = "GPLv2+"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = ("gstreamer-1.0/1.14.4@conanos/dev", "gst-plugins-base-1.0/1.14.4@conanos/dev","json-glib/1.4.4@conanos/dev",
                
                "orc/0.4.28@conanos/dev","gobject-introspection/1.58.0@conanos/dev","gst-rtsp-server/1.14.4@conanos/dev",
                "libffi/3.3-rc0@conanos/dev","glib/2.58.0@conanos/dev",)

    source_subfolder = "source_subfolder"
    remotes = {'origin': 'https://github.com/GStreamer/gst-devtools.git'}

    def source(self):
        #tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version))
        #extracted_dir = "gst-devtools-" + self.version
        #os.rename(extracted_dir, self.source_subfolder)
        tools.mkdir(self.source_subfolder)
        with tools.chdir(self.source_subfolder):
            self.run('git init')
            for key, val in self.remotes.items():
                self.run("git remote add %s %s"%(key, val))
            self.run('git fetch --all')
            self.run('git reset --hard %s'%(self.version))
            self.run('git submodule update --init --recursive')

    def build(self):
        with tools.chdir(self.source_subfolder):
            with tools.environment_append({
                'PATH':'%s/bin:%s'%(self.deps_cpp_info["gobject-introspection"].rootpath,os.getenv("PATH")),
                'C_INCLUDE_PATH':'%s/include/gstreamer-1.0:%s/include/gstreamer-1.0'
                %(self.deps_cpp_info["gst-rtsp-server"].rootpath,self.deps_cpp_info["gst-plugins-base-1.0"].rootpath),
                'LD_LIBRARY_PATH':'%s/lib'%(self.deps_cpp_info["libffi"].rootpath)
                }):
                meson = Meson(self)
                meson.configure(
                    defs={ 'disable_introspection':'false',
                           'prefix':'%s/builddir/install'%(os.getcwd()), 'libdir':'lib',
                         },
                    source_dir = '%s'%(os.getcwd()),
                    build_dir= '%s/builddir'%(os.getcwd()),
                    pkg_config_paths=[ '%s/lib/pkgconfig'%(self.deps_cpp_info["gstreamer-1.0"].rootpath),
                                       '%s/lib/pkgconfig'%(self.deps_cpp_info["gst-plugins-base-1.0"].rootpath),
                                       '%s/lib/pkgconfig'%(self.deps_cpp_info["json-glib"].rootpath),
                                       '%s/lib/pkgconfig'%(self.deps_cpp_info["orc"].rootpath),
                                       '%s/lib/pkgconfig'%(self.deps_cpp_info["gst-rtsp-server"].rootpath),
                                      ]
                                )
                meson.build(args=['-j4'])
                self.run('ninja -C {0} install'.format(meson.build_dir))


    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir/install"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

