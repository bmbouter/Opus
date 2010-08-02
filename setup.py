from distutils.core import setup

setup(
    name='Opus',
    version='0.1',
    url="https://fedorahosted.org/opus/",
    maintainer="ITng Services",
    maintainer_email="",
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
    license='Apache License 2.0',
    long_description=open("README.txt",'r').read(),
)
