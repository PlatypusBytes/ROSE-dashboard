import numpy as np
import json
from rose.pre_process.default_trains import TrainType, set_train, train_class_to_dict


def read_sos_data(path_sos_json):
    """
    Reads sos json file

    :param path_sos_json: path to the sos json file
    :return: sos data dictionary
    """
    with open(path_sos_json, 'r') as f:
        sos_data = json.load(f)
    return sos_data


def train_model(time, velocity, start_coord):
    """
    Creates train model structure

    :param time: time vector
    :param velocity: train velocity
    :param start_coord: start coordinate
    :return: train model dictionary
    """

    sprinter = set_train(time, velocity, start_coord, TrainType.SPRINTER_SGM)
    intercity = set_train(time, velocity, start_coord, TrainType.DOUBLEDEKKER)
    traxx = set_train(time, velocity, start_coord, TrainType.TRAXX)
    cargo = set_train(time, velocity, start_coord, TrainType.CARGO_SGNS)

    trains = {"Sprinter": {"model": sprinter,
                           "traffic": {"nb-per-hour": 4,
                                       "nb-hours": 16,
                                       "nb-axles": 16}},
              "Intercity": {"model": intercity,
                            "traffic": {"nb-per-hour": 4,
                                        "nb-hours": 16,
                                        "nb-axles": 16}},
              "Traxx": {"model": traxx,
                        "traffic": {"nb-per-hour": 4,
                                    "nb-hours": 16,
                                    "nb-axles": 16}},
              "Cargo": {"model": cargo,
                        "traffic": {"nb-per-hour": 27,
                                    "nb-hours": 1,
                                    "nb-axles": 10 * 4}},
            }

    return trains


def geometry(nb_sleeper):
    """
    Sets track geometry parameters

    :param nb_sleeper: number of sleepers per segment
    :return: geometry dictionary
    """
    # Set geometry parameters
    geometry = {}
    geometry["n_segments"] = len(nb_sleeper)
    geometry["n_sleepers"] = nb_sleeper  # number of sleepers per segment
    geometry["sleeper_distance"] = 0.6  # distance between sleepers, equal for each segment
    geometry["depth_soil"] = [1.]  # depth of the soil [m] per segment

    geometry["sleeper_length"] = 3.5
    geometry["sleeper_width"] = 0.25
    return geometry


def materials():
    """
    Sets track material parameters

    :return: material dictionary
    """
    material = {}
    # set parameters of the rail
    material["young_mod_beam"] = 210e9  # young modulus rail
    material["poisson_beam"] = 0.0  # poison ration rail
    material["inertia_beam"] = 2.24E-05  # inertia of the rail
    material["rho"] = 7860.  # density of the rail
    material["rail_area"] = 69.6e-2  # area of the rail
    material["shear_factor_rail"] = 0.  # Timoshenko shear factor

    # Rayleigh damping system
    material["damping_ratio"] = 0.02  # damping
    material["omega_one"] = 6.283  # first radial_frequency
    material["omega_two"] = 125.66  # second radial_frequency

    # set parameters rail pad
    material["mass_rail_pad"] = 5.  # mass of the rail pad [kg]
    material["stiffness_rail_pad"] = 750e6  # stiffness of the rail pad [N/m2]
    material["damping_rail_pad"] = 750e3  # damping of the rail pad [N/m2/s]

    # set parameters sleeper
    material["mass_sleeper"] = 140.  # [kg]

    # set up contact parameters
    material["hertzian_contact_coef"] = 9.1e-7  # Hertzian contact coefficient
    material["hertzian_power"] = 3 / 2  # Hertzian power

    return material


def time_integration():
    """
    Sets time integration data

    :return: time dictionary
    """
    time = {}

    # set time parameters in two stages
    time["tot_ini_time"] = 0.5  # total initalisation time  [s]
    time["n_t_ini"] = 5000  # number of time steps initialisation time  [-]

    time["tot_calc_time"] = 1.0  # total time during calculation phase   [s]
    time["n_t_calc"] = 8000  # number of time steps during calculation phase [-]

    time["cumulative_time"] = 365 # cumulative time for the calculation [days]
    return time


def create_dash_input_json(path_sos_json, embankment_data, path_output_json, project_name="ROSEcalculations"):
    """
    Creates input json file for the dashboard

    :param path_sos_json: path to the sos json file
    :param embankment_data: embankment data
    :param path_output_json: path to the output json file
    :param project_name: name of the project
    """
    # reads sos data
    sos_data = read_sos_data(path_sos_json)

    # set time integration and track information
    time_data = time_integration()
    track_materials = materials()
    track_geometry = geometry([140])

    track_info = {"geometry": track_geometry,
                  "materials": track_materials}

    # get default trains
    trains = train_model(np.nan, np.nan, 30.)

    # convert default train class to dictionaries
    train_dicts = [train_class_to_dict(train["model"]) for train in trains.values()]

    # add equal train velocity and train type to each default train
    train_velocity = 100 / 3.6
    for i, train in enumerate(train_dicts):
        train["velocity"] = train_velocity
        train["type"] = list(trains.keys())[i]
        train["traffic"] = list(trains.values())[i]["traffic"]

    # convert train list to dict
    train_dicts = {train_nbr: train_dicts[train_nbr] for train_nbr in range(len(train_dicts))}

    new_sos_dict = {}
    for k, v in sos_data.items():
        segment_name = k
        coordinates = list(v.values())[0]['coordinates']
        scenarios = {}
        for k2, v2 in v.items():
            scenario = k2
            probability = v2["probability"]
            soil_layers = v2["soil_layers"]
            scenarios[scenario] = {"probability": probability,
                                   "soil_layers": soil_layers,
                                   }

        new_sos_dict[segment_name] = {"coordinates": coordinates,
                                      "scenarios": scenarios,
                                      "embankment": embankment_data,
                                      "construction_time": 50,  # construction time [years]
                                      }

    input_dict = {"project_name": project_name,
                  "sos_data": new_sos_dict,
                  "traffic_data": train_dicts,
                  "track_info": track_info,
                  "time_integration": time_data}

    with open(path_output_json, 'w') as json_file:
        json.dump(input_dict, json_file, indent=2)


if __name__ == '__main__':
    # set embankment data
    E = 100e6
    v = 0.2
    emb = ["embankment", E / (2 * (1 + v)), v, 2000, 0.05, 0.8]
    create_dash_input_json(r"data_SoS/SOS.json", emb, 'example_rose_input.json')
