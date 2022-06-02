#%%
class Aliasor:
    def __init__(self, alias_file=None):
        import pandas as pd

        if alias_file is None:
            # import importlib.resources

            aliases = pd.read_json("https://raw.githubusercontent.com/cov-lineages/pango-designation/master/pango_designation/alias_key.json")
            # with importlib.resources.open_text("pango_designation", "alias_key.json") as file:
            #     aliases = pd.read_json(file)

        else:
            aliases = pd.read_json(alias_file)

        self.alias_dict = {}
        for column in aliases.columns:
            if column.startswith('X'):
                self.alias_dict[column] = column
            else:
                self.alias_dict[column] = aliases[column][0]

        self.alias_dict['A'] = 'A'
        self.alias_dict['B'] = 'B'

        self.realias_dict = {v: k for k, v in self.alias_dict.items()}

    def compress(self,name):
        name_split = name.split('.')
        levels = len(name_split) - 1
        num_indirections = (levels -1) // 3
        if num_indirections <= 0:
            return name
        alias = ".".join(name_split[0:(3*num_indirections + 1)])
        ending = ".".join(name_split[(3*num_indirections + 1):])
        return self.realias_dict[alias] + '.' + ending

    def uncompress(self,name):
        name_split = name.split('.')
        letter = name_split[0]
        try:
            unaliased = self.alias_dict[letter]
        except KeyError:
            return name
        if len(name_split) == 1:
            return name
        if len(name_split) == 2:
            return unaliased + '.' + name_split[1]
        else:
            return unaliased + '.' + ".".join(name_split[1:])
# %%
