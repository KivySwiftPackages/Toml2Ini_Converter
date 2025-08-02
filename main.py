from tomllib import load as tomllib_load
from configparser import ConfigParser
from pprint import pprint


def toml2config_parser(pyproject: str) -> ConfigParser:
    ini = ConfigParser()
    with open(pyproject, "rb") as f:
        toml = tomllib_load(f)

    # Convert the relevant sections from the TOML file to INI format
    bz = toml["buildozer-app"]
    ini.add_section("app")
    def unpack_children(ini: ConfigParser, root_key: str, value: object):
        match value:
            case str():
                ini.set("app", root_key, value )
            case list():
                ini.set("app", root_key, ", ".join(value))
            case dict():
                for k, v in value.items():
                    unpack_children(ini, f"{root_key}.{k}", v)
            case _:
                ini.set("app", root_key, str(value))

    requirements: list[str] = bz.pop("requirements")
    for key, value in bz.items():
        unpack_children(ini, key, value)
    
    toml_proj: dict = toml["project"]
    toml_deps: list[str] = toml_proj["dependencies"]
    toml_android: list[str] = toml["dependency-groups"]["android"]
    requirements = requirements + toml_deps + toml_android
    unpack_children(ini, "requirements", requirements)

    return ini

def convert(_input: str, _output: str):
    ini = toml2config_parser(_input)

    with open(_output, "w") as f:
        ini.write(f)


if __name__ == "__main__":
    from sys import argv
    convert(argv[1], argv[2])
