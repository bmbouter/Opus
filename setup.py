import os.path

from distutils.core import setup

# Install data_files for gwtmedia directory
data_files = []
tocopy = os.path.join("gwt","build")
for dirpath, dirnames, filenames in os.walk(tocopy):
    if filenames:
        if dirpath.startswith(tocopy):
            ndirpath = dirpath[len(tocopy):]
        if ndirpath.startswith(os.path.sep):
            ndirpath = ndirpath[1:]
        data_files.append(
                (
                    os.path.join("share","opus","media",ndirpath),
                    [os.path.join(dirpath,x) for x in filenames],
                )
        )


if __name__ == "__main__":
    setup(
        name='Opus',
        version='0.1',
        url="https://fedorahosted.org/opus/",
        maintainer="North Carolina State University",
        maintainer_email="opus-devel@lists.fedorahosted.org",
        platforms=["Linux"],
        packages=[
            'opus',
            'opus.lib',
            'opus.lib.conf',
            'opus.lib.deployer',
            'opus.lib.profile',
            'opus.lib.profile.profilerapp',
            'opus.lib.prov',
            'opus.lib.builder',
            'opus.lib.osutils',
            'opus.project',
            'opus.project.deployment',
            'opus.project.dcmux',
            ],
        package_data = {
            'opus.project': ['settings.py.sample',
                             'templates/*.html',
                             'templates/deployment/*.html',
                             'templates/registration/*.html',
                             ],
            'opus.project.dcmux': ['templates/*.xml'],
            'opus.lib.conf': ['default_settings.json'],
            },
        data_files = data_files,
        license='Apache License 2.0',
        long_description=open("README.txt",'r').read(),
    )
