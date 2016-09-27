package(default_visibility = ["//visibility:public"])

load("@org_pubref_rules_protobuf//python:rules.bzl", "py_proto_compile")

py_proto_compile(
	name = "my_proto",
	protos = ["my.proto"],
	verbose = 1,
)

py_binary(
    name = "xml_parser",
    srcs = [
        "xml_parser.py",
        ":my_proto"
    ],
    main = "xml_parser.py",
)
