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
    
    def partial_compress(self, name, up_to: int = 0, accepted_aliases: set = {}):
        """
        aliasor.partial_compress("B.1.1.529.3.1",up_to=1) # 'BA.3.1'
        aliasor.partial_compress("B.1.1.529.3.1.1.2",up_to=1) # 'BA.3.1.1.2'

        aliasor.partial_compress("B.1.1.529.3.1",accepted_aliases=["AY"]) # 'B.1.1.529.3.1'
        aliasor.partial_compress("B.1.617.2",accepted_aliases=["AY"]) # 'AY.2'
        """
        # If accepted_aliases is passed without up_to set, then try out all possible values
        name_split = name.split(".")
        levels = len(name_split) - 1
        indirections = (levels - 1) // 3

        alias = name_split[0]

        if up_to > 0:
            if indirections <= up_to:
                return self.compress(name)
            to_alias = ".".join(name_split[0 : (3 * up_to + 1)])
            alias = self.realias_dict[to_alias]
        
        # Compress at least till up_to, maybe further

        # Check if levels beyond up_to (working backwards) are in accepted_aliases
        if accepted_aliases is not {}:
            for level in range(indirections,up_to,-1):
                to_alias = ".".join(name_split[0 : (3 * level + 1)])
                if to_alias in self.realias_dict.keys():
                    if self.realias_dict[to_alias] in accepted_aliases:
                        alias = self.realias_dict[to_alias]
                        return alias + "." + ".".join(name_split[(3 * level + 1) :])

        return alias + "." + ".".join(name_split[(3 * up_to + 1) :])


# %%
