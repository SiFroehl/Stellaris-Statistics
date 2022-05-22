import os
import time
import json
import logging
import numpy as np

USUALLY_SKIPPED_KEYS = ['species', 'half_species', 'last_created_species', 'nebula', 'pop', 'last_created_pop',
                        # "galactic_object",
                        'starbases', 'planets', 'alliance', 'truce', 'trade_deal',
                        'last_created_country', 'last_refugee_country', 'last_created_system', 'leaders',
                        'saved_leaders', 'ships', 'fleet', 'fleet_template', 'last_created_fleet',
                        'last_created_ship', 'last_created_leader', 'last_created_army',
                        'last_created_design', 'army', 'deposit', 'ground_combat', 'fired_events',
                        'war', 'debris', 'missile', 'strike_craft', 'ambient_object',
                        'last_created_ambient_object', 'message', 'last_diplo_action_id',
                        'last_notification_id', 'last_event_id', 'random_name_database', 'name_list',
                        'galaxy', 'galaxy_radius', 'flags', 'saved_event_target', 'ship_design',
                        'pop_factions', 'last_created_pop_faction', 'last_killed_country_name',
                        'megastructures', 'bypasses', 'natural_wormholes', 'trade_routes', 'sectors',
                        'buildings', 'archaeological_sites', 'global_ship_design', 'clusters',
                        'rim_galactic_objects', 'used_color', 'used_symbols', 'used_species_names',
                        'used_species_portrait', 'random_seed', 'random_count',
                        'trade_routes_manager', 'slave_market_manager']


def create_dict_from_file(file_name, skipped_top_level_keys=[]):
    logging.info("create_dict_from_file")
    file = open(file_name, "r")
    root = dict()
    nest = [root]
    unnamed = 0
    for line in file:
        try:
            if "{" in line:
                key = line.split("=")[0].strip()
                if "=" not in line:
                    key = "unnamed_key%i" % unnamed
                    unnamed += 1
                nd = dict()
                nest[-1][key] = nd
                nest.append(nd)
            if "}" in line:
                nest.pop(-1)
            if "=" in line and "{" not in line:
                key = line.split("=")[0].strip()
                val = line.split("=")[1].strip()
                nest[-1][key] = val
        except:
            logging.warn("Error while parsing save file!")
            logging.warn(nest)
            logging.warn(line)
    file.close()
    for skipped_key in skipped_top_level_keys:
        if skipped_key in root.keys():
            skipped = 0
            if type(root[skipped_key]) == dict:
                skipped = len(root[skipped_key].keys())
            root[skipped_key] = "Skipped %i entries" % skipped
    return root


def create_json_from_file(file, out_file, skipped_top_level_keys=[]):
    logging.info("create_json_from_file")
    root = create_dict_from_file(file, skipped_top_level_keys)
    dir_name = "/".join(out_file.split("/")[:-1]) + "/"
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    f_out = open(out_file, "w")
    json.dump(root, f_out, indent=2)
    f_out.close()




def create_empire_base_array(save_game, empire_id, observed_resources=None, meta_dict=None, print_dict=None, default_print=False):
    """
    Creates an "empire base array" for the given save game and empire. This array is an N_s x N_r x 3 array with 
        N_s = Number of save files
        N_r = Number of resources, equal to len(observed_resources) if given
    This will contain the resource income ([:,:,0]), expenses ([:,:,1]) and balance ([:,:,2])
    save_game: string, the save game to create the array for
    empire_id: string or int, the id of the empire to create the array for (player empires are 0 by default)
    observed_resources: list or None, if list then only resources in the list will be added to the array,
                        if None, all will be added
    meta_dict: None or dict, if None, all game_dicts will be loaded from file, if meta_dict, the pre_loaded
               game_dicts will be used if possible
    
    returns: numpy array, the base array
             dict, the dict for conversion between resource names and indices in the array
    """
    if type(observed_resources) is dict:
        print("Observed resources should be a list and will cause unexpected results with a dict. Are you sure you did not mean it as the meta_dict?")
    t0 = time.time_ns()
    if observed_resources is None:
        observed_resources = ["energy", "minerals", "food", "consumer_goods", "alloys", "physics_research", "society_research",
                              "engineering_research", "influence", "unity", "exotic_gases", "volatile_motes", "rare_crystals",
                              "sr_dark_matter", "sr_living_metal", "sr_zro"]

    observed_resource_dict = {name:i for i,name in enumerate(observed_resources)}
        
    
    empire_id = str(empire_id)
    files = os.listdir(save_game + "/copied_saves")
    
    jsons = [f for f in files if f.endswith(".json")]
    num_jsons = len(jsons)
    num_resources = len(observed_resources)
    
    arr = np.zeros((num_jsons,num_resources,3))
    
    not_observed = []
    
    for i,file in enumerate(jsons):
        try:
            game_dict = None
            if meta_dict is not None:
                if file in meta_dict:
                    game_dict = meta_dict.get(file)
                
            if game_dict is None:
                game_dict = json.load(open(save_game + "/copied_saves/" + file))
                if meta_dict is not None:
                    print("Using fallback for save %s" % file)
            if empire_id not in game_dict["country"].keys():
                if print_dict is not None and print_dict.get("print_missing_empire_warning",default_print):
                    print("The save game %s did not contain the requested empire. This may be due to them not (yet) existing [anymore]" % file)
                continue
            
            empire = game_dict["country"][empire_id]
            if type(empire) is not dict:
                # Not a real empire -> no economy
                if print_dict is not None and print_dict.get("print_irregular_empire_error",default_print):
                    print(type(empire),empire)
                    print("Empire with id %s does not have an empire module and will be skipped" % empire_id)
                continue
            budget = empire["budget"]
            current_month = budget["current_month"]
            keys = ["income", "expenses", "balance"]
            for j,key in enumerate(keys):
                to_process = current_month[key]
                for sub_dict in to_process.values():
                    for resource_type, amount in sub_dict.items():
                        if resource_type in observed_resources:
                            arr[i,observed_resource_dict[resource_type],j] += float(amount)
                        else:
                            if resource_type not in not_observed:
                                not_observed.append(resource_type)
            if print_dict is not None and print_dict.get("print_progress",default_print):
                print("Processed %i/%i [%i %s]" % (i,num_jsons,100*i/num_jsons,"%"), end="\r")
        except FileNotFoundError as e:
            # This should not happen as the file names are generated in a way that ensures their existence
            # Maybe the files were renamed/moved/removed since the files list was created
            print("File not found for %s, it may have been renamed/moved/removed since the conversion was started" % file)
            print(e)
        except json.JSONDecodeError as e:
            # This should also not happen as the copy script outputs json files via the json-library
            # Maybe the copy_script has not finished writing?
            print("The file %s seems to be corrupted, this might be due to the copy_script being interrupted forcefully" % s)
            print(e)
        
    T = time.time_ns()
    if print_dict is not None and print_dict.get("print_time",default_print):
        print("Took %.3f s to create base array" % ((T-t0)/1e9), " "*20)
    if len(not_observed) > 0:
        print("There were %i unobserved resource types:" % len(not_observed),not_observed)
    return arr, observed_resource_dict

def extend_empire_base_array(base, res_dict, print_dict=None, default_print=False):
    """
    Extends the base data array for an empire by the additional metrics 
        "unified_resource" -> converts all resources into their energy equivalent (does not include research & unity)
        "unified_product"  -> converts all products into their energy equivalent (includes research & unity)
    base: numpy array, the base array to extend, resources that are not contained will not be inclueded in the conversion (count as 0)
    res_dict: dict, the dictionairy to convert between indices in the array and resource names
    
    returns: numpy array, the extended array with size base.shape + [0,2,0]
             dict, the extended dict with the additional keys "unified_resource" and "unified_product"
    """
    t0 = time.time_ns()
    extended = np.zeros((base.shape[0],base.shape[1]+2,base.shape[2]))
    extended[:,:-2,:] = base
    new_res_dict = dict(res_dict)
    new_res_dict["unified_resource"] = base.shape[1]
    new_res_dict["unified_product"] = base.shape[1] + 1
    unified_resource_conversion = {
    "minerals": 1, "energy": 1, "food": 1, "consumer_goods": 2, "alloys": 4, "exotic_gases": 10, "volatile_motes": 10,
    "rare_crystals": 10, "sr_dark_matter": 20, "sr_living_metal": 20, "sr_zro": 20
    }
    unified_product_conversion = {
    "minerals": 1, "energy": 1, "food": 1, "consumer_goods": 2, "alloys": 4, "exotic_gases": 10, "volatile_motes": 10,
    "rare_crystals": 10, "sr_dark_matter": 20, "sr_living_metal": 20, "sr_zro": 20, "unity": 2, "physics_research": 1/3,
    "society_research": 1/3, "engineering_research": 1/3
    }
    ur_conversion_ = np.array([unified_resource_conversion.get(key,0) for key in res_dict.keys()])
    up_conversion_ = np.array([unified_product_conversion.get(key,0) for key in res_dict.keys()])
    ur_conversion = np.zeros_like(base)
    up_conversion = np.zeros_like(base)
    for i in range(len(ur_conversion_)):
        ur_conversion[:,i,:] = ur_conversion_[i]
        up_conversion[:,i,:] = up_conversion_[i]
    extended[:,base.shape[1],:] = np.sum(base*ur_conversion, axis=1)
    extended[:,base.shape[1]+1,:] = np.sum(base*up_conversion, axis=1)
    T = time.time_ns()
    if print_dict is not None and print_dict.get("print_time",default_print):
        print("Extended array in %.3f s" % ((T-t0)/1e9))
    return extended, new_res_dict

def get_time_conversion(save_game):
    """
    Generates an array with the in game times for the saves in the selected save game.
    For example, a save game with quarterly autosaves will result in [2200.0,2200.25,2200.5,2200.75,...]
    save_game: string, the save game to generate the conversion for
    
    returns: numpy array, the conversion between index and time
    """
    files = os.listdir(save_game + "/copied_saves")
    jsons = [f for f in files if f.endswith(".json")]
    conversion = np.zeros(len(jsons),dtype=float)
    for i,file in enumerate(jsons):
        inp = open(save_game + "/copied_saves/" + file)
        date = None
        for line in inp:
            if '"date": ' in line:
                #print(line)
                date = line.split(":")[1].replace(",","").replace('"',"").replace("\\","").strip()
                break
        split = date.split(".")
        conversion[i] = int(split[0]) + (int(split[1])-1 + (int(split[2])-1)/30)/12
    return conversion


def load_all_game_dicts(save_game, print_dict=None, default_print=False):
    """
    Loads all game_dicts into a single 'meta_dict' for later use to avoid reloading them every time.
    Can use multiple GB of RAM so use with caution!
    Only usefull if the meta_dict is used multiple times (for instance when comparing different empires within a save)
    save_game: string, name of the save game to load
    
    returns: dict of dicts which are themselves the game_dicts, this will be called meta_dict
    """
    t0 = time.time_ns()
    meta_dict = dict()
    files = os.listdir(save_game + "/copied_saves")
    jsons = [f for f in files if f.endswith(".json")]
    num_jsons = len(jsons)
    for i, file in enumerate(jsons):
        game_dict = json.load(open(save_game + "/copied_saves/" + file))
        meta_dict[file] = game_dict
        print("Processed %i/%i [%i %s]" % (i,num_jsons,100*i/num_jsons,"%"), end="\r")
    T = time.time_ns()
    if print_dict is not None and print_dict.get("print_time",default_print):
        print("Took %.3f s to generate meta_dict" % ((T-t0)/1e9), " "*20)
    return meta_dict

def get_all_empires(meta_dict, has_budget_module=True):
    """
    Generates two dicts of empire names to empire ids and visa versa for all empires in the meta_dict
    Empires with game generated names have a more complex way to save the name (prob. due to translation), this is not implemented yet and will just give the id
    This makes this function only usefull for empires with custom names (most player empires) and to get all valid ids
    meta_dict: The meta_dict for the save game (generated by load_all_game_dicts)
    has_budget_module: bool, wether to return only empires with a budget module (real empires)
    
    returns: dict, Maps empire names to empire ids
             dict, Maps empire ids to empire names
    """
    id_to_name = dict()
    for game_dict in meta_dict.values():
        country = game_dict["country"]
        for empire_id in country.keys():
            if empire_id not in id_to_name.keys():
                try:
                    if type(country[empire_id]) is not dict:
                        continue
                    name = country[empire_id]["name"]
                    if len(name) == 1:
                        name = name["key"]
                    else:
                        # More complex, just use id for now
                        name = empire_id
                    
                    if (not has_budget_module) or ("budget" in country[empire_id].keys()):
                        id_to_name[empire_id] = name
                except Exception as e:
                    print(e)
                    print(empire_id)
                    print(country[empire_id])
                    break
    return {v:k for k,v in id_to_name.items()}, id_to_name
