#%%
class Aliasor:
    def __init__(self, alias_file=None):
        import json

        if alias_file is None:
            import urllib.request, json

            with urllib.request.urlopen(
                "https://raw.githubusercontent.com/cov-lineages/pango-designation/master/pango_designation/alias_key.json"
            ) as data:
                file = json.load(data)

        else:
            with open(alias_file) as file:
                file = json.load(file)

        self.alias_dict = {}
        for column in file.keys():
            if type(file[column]) is list or file[column] == "":
                self.alias_dict[column] = column
            else:
                self.alias_dict[column] = file[column]

        self.realias_dict = {v: k for k, v in self.alias_dict.items()}

    def compress(self, name):
        name_split = name.split(".")
        levels = len(name_split) - 1
        num_indirections = (levels - 1) // 3
        if num_indirections <= 0:
            return name
        alias = ".".join(name_split[0 : (3 * num_indirections + 1)])
        ending = ".".join(name_split[(3 * num_indirections + 1) :])
        return self.realias_dict[alias] + "." + ending

    def uncompress(self, name):
        name_split = name.split(".")
        letter = name_split[0]
        try:
            unaliased = self.alias_dict[letter]
        except KeyError:
            return name
        if len(name_split) == 1:
            return name
        if len(name_split) == 2:
            return unaliased + "." + name_split[1]
        else:
            return unaliased + "." + ".".join(name_split[1:])


# %%
