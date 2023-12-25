import pandas as pd


# Pre-process the CSV of exoplanet data
def gather_exoplanet_attributes(nasa_exoplanet_archive):
    # Read NASA exoplanet planetary systems table
    exoplanet_data = pd.read_csv(nasa_exoplanet_archive, header=0, skiprows=list(range(0, 96)))

    # Drop rows with 'NaN' in any of the rows we will use
    exoplanet_data.dropna(subset=['sy_snum', 'sy_pnum', 'discoverymethod', 'disc_year', 'pl_controv_flag', 'pl_orbper',
                                  'pl_bmasse', 'pl_orbeccen', 'st_teff', 'st_met', 'st_mass', 'st_logg', 'sy_dist',
                                  'sy_kmag'], inplace=True)

    # Remove rows with discovery methods that do not occur more than once in the entire dataset
    method_counts = exoplanet_data['discoverymethod'].value_counts()
    valid_methods = method_counts[method_counts > 20].index
    exoplanet_data = exoplanet_data[exoplanet_data['discoverymethod'].isin(valid_methods)]

    # Set values for use in encoding color for controversial status row 1 of visualization later
    exoplanet_data['pl_controv_flag'] = exoplanet_data['pl_controv_flag'].apply(
        lambda x: "not controversial" if x == 0 else "controversial")

    return exoplanet_data

