from cpt.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds()

    transformed_builds = []
    for settings, options, env_vars, build_requires, reference in builder.items:
        if settings["compiler"] != "Visual Studio":
            options["zziplib:shared"] = "True"
            transformed_builds.append([settings, options, env_vars, build_requires, reference])
            options2 = options.copy()
            options2["zziplib:shared"] = "False"
            transformed_builds.append([settings, options2, env_vars, build_requires, reference])
        else:
            try:
                del options["zziplib:shared"]
            except:
                pass
            transformed_builds.append([settings, options, env_vars, build_requires, reference])

    if transformed_builds:
        builder.builds = transformed_builds

    builder.run()
