[
    py_binary(
        name = (str(filename.split('/')[-1]))[:-3],
        srcs = [filename],
        deps = ["sim"],
    #    imports = ["."]
    )
    for filename in glob(["sim/experiments/**/*.py"])
]

py_library(
    name = "sim",
    srcs = glob(["sim/*.py"]),
    deps = ["platforms"],
)

py_library(
    name = "platforms",
    srcs = glob(["sim/platforms/*.py"]),
    deps = [],
)