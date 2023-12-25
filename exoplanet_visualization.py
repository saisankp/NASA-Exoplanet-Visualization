from textwrap import wrap
import altair as alt
import pandas as pd

from exoplanet_data_preprocessing import gather_exoplanet_attributes


# Plot in row one showing that as exoplanet discoveries have been further away over time from earth.
def distance_versus_discovery(nasa_exoplanet_archive):
    # Get data for a blue trend line (median of the top 10% of distances each year)
    nasa_exoplanet_archive['top_10_percent'] = nasa_exoplanet_archive.groupby('disc_year')['sy_dist'].transform(
        lambda x: x.quantile(0.9)
    )
    top_10_percent_data = nasa_exoplanet_archive[
        nasa_exoplanet_archive['sy_dist'] >= nasa_exoplanet_archive['top_10_percent']]
    median_top_10_percent = top_10_percent_data.groupby('disc_year')['sy_dist'].median()
    df = pd.DataFrame(list(median_top_10_percent.items()), columns=['Year', 'Distance'])
    trend_line = alt.Chart(df, title=alt.TitleParams(
        text="Are we finding exoplanets further away and do they cause controversy? ",
        fontSize=25, font='Courier New')).mark_line(color='blue').encode(
        x=alt.X("Year:O"),
        y=alt.Y("Distance:Q"),
        tooltip=[alt.Tooltip("Distance", title="Name of controversial exoplanet")]
    ).properties(width=1200, height=400)

    # Color scheme for encoding color
    color_scheme = {"controversial": "red", "not controversial": "green"}

    # Create a scatter plot for green points (not controversial)
    green_points = alt.Chart(nasa_exoplanet_archive).mark_point().encode(
        x=alt.X('disc_year:O', title='Year of exoplanet discovery', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('sy_dist:Q', title='Distance to the planetary system from earth (Parsec)'),
        # Encoding color as the status of controversy
        color=alt.Color("pl_controv_flag:O",
                        scale=alt.Scale(domain=list(color_scheme.keys()), range=list(color_scheme.values())),
                        legend=alt.Legend(title="Literature opinion", orient='right')),
        # Encoding shape as the discovery method
        shape=alt.Shape("discoverymethod", legend=alt.Legend(title="Discovery method", orient='right')),
        size=alt.value(100),
        tooltip=[alt.Tooltip("pl_name", title="Name of exoplanet"), alt.Tooltip("sy_dist", title="Distance from earth"),
                 alt.Tooltip("disc_year", title="Year of discovery")]
    ).transform_filter(alt.datum.pl_controv_flag == "not controversial")

    # Create a scatter plot for red points (controversial)
    red_points = alt.Chart(nasa_exoplanet_archive).mark_point().encode(
        x=alt.X('disc_year:O', title='Year of exoplanet discovery', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('sy_dist:Q', title='Distance to the planetary system from earth (Parsec)'),
        color=alt.Color("pl_controv_flag:O",
                        scale=alt.Scale(domain=list(color_scheme.keys()), range=list(color_scheme.values())),
                        legend=None),
        # Encoding shape as the discovery method
        shape=alt.Shape("discoverymethod", legend=alt.Legend(title="Discovery method")),
        size=alt.value(400),
        tooltip=[alt.Tooltip("pl_name", title="Name of controversial exoplanet"),
                 alt.Tooltip("sy_dist", title="Distance from earth"),
                 alt.Tooltip("disc_year", title="Year of discovery")]
    ).transform_filter(alt.datum.pl_controv_flag == "controversial")

    # Layer the red and green points along with the blue trend line
    scatter_plot = alt.layer(green_points, red_points, trend_line).properties(width=1200, height=400)

    return scatter_plot


# Plot in row 2 to show that the brightness of an exoplanet's host star increases as the exoplanet is further away
def distance_versus_star_brightness(nasa_exoplanet_archive):
    plot = alt.Chart(nasa_exoplanet_archive, title=alt.TitleParams(
        text=wrap("As exoplanets are further away, is their host star brighter?", 31),
        fontSize=15, font='Courier New')).mark_circle().encode(
        y=alt.X('sy_kmag:Q', title='Brightness of host star (Magnitude)'),
        x=alt.Y('sy_dist:Q', title='Distance to the planetary system (Parsec)'),
        tooltip=[alt.Tooltip("sy_kmag", title="Brightness of host star"),
                 alt.Tooltip("sy_dist", title="Distance from exoplanet")]
    ).properties(width=357, height=350)
    return plot


# Plot in row 2 to show that the range of brightness from the exoplanet's host star decreases with the number of planets
def range_of_star_brightness_versus_number_of_planets_in_planetary_system(nasa_exoplanet_archive):
    # Get the range of brightness for each number of planets by aggregating the data
    result_df = pd.DataFrame()
    for i in nasa_exoplanet_archive['sy_pnum'].unique():
        copy = nasa_exoplanet_archive[nasa_exoplanet_archive['sy_pnum'] == i]
        brightness_range = copy.groupby('sy_pnum')['sy_kmag'].agg(lambda x: x.max() - x.min()).reset_index()
        brightness_range.columns = ['sy_pnum', 'brightness_range']
        result_df = pd.concat([result_df, brightness_range], ignore_index=True)
    nasa_exoplanet_archive['new_brightness_range'] = nasa_exoplanet_archive['sy_pnum'].apply(
        lambda x: result_df.loc[result_df['sy_pnum'] == x, 'brightness_range'].values[0]
    )
    horizontal_bar_graph = alt.Chart(nasa_exoplanet_archive, title=alt.TitleParams(
        text=wrap("Does the host star's brightness suit particular numbers of planets?", 35),
        fontSize=15, font='Courier New')).mark_rule(strokeWidth=5, color="purple").encode(
        y=alt.X('sy_pnum:Q', title='Number of planets in the planetary system', scale=alt.Scale(
            domain=[0, nasa_exoplanet_archive["sy_pnum"].max() + 0.5])),
        x=alt.X('min(sy_kmag):Q', title='Range of brightness of host star (Magnitude)'),
        x2='max(sy_kmag):Q',
        tooltip=[alt.Tooltip("sy_pnum", title="Number of planets"),
                 alt.Tooltip("new_brightness_range:Q", title="Host star's brightness range")]
    ).properties(width=357, height=350)
    return horizontal_bar_graph


# Plot in row 2 to show that the mass of an exoplanet decreases when the number of planets increases
def number_of_planets_in_planetary_system_versus_planet_mass_versus(nasa_exoplanet_archive):
    vertical_bar_chart = alt.Chart(nasa_exoplanet_archive, title=alt.TitleParams(
        text=wrap("As the number of planets increases, does the exoplanet's mass decrease?", 35),
        fontSize=15, font='Courier New')).mark_rect(strokeWidth=48, color='black').encode(
        y=alt.X('count(pl_bmasse):Q', title="Exoplanet's mass (M⊕)"),
        x=alt.Y('sy_pnum:O', title='Number of planets in the planetary system'),
        tooltip=[alt.Tooltip("max(pl_bmasse)", title="Total mass of exoplanets"),
                 alt.Tooltip("sy_pnum:Q", title="Number of planets in the planetary system")]
    ).properties(width=357, height=350)
    return vertical_bar_chart


# Plot in row 3 to show that dips in the mean metallic content on exoplanet's stars align with years of controversy
def average_metal_content_of_star_versus_discovery(nasa_exoplanet_archive):
    # Get mean of metallic content of all discoveries by year
    metallic_content = pd.DataFrame(
        {'year': nasa_exoplanet_archive['disc_year'], 'y': nasa_exoplanet_archive['st_met']})
    mean_metallic_content = metallic_content.groupby('year')['y'].mean().reset_index()

    # Surplus/deficit filled line
    chart = alt.Chart(mean_metallic_content, title=alt.TitleParams(
        text=wrap(
            "Does the decrease in mean metal content of an exoplanet's star align with the years that "
            "controversial discoveries happened from before?", 68),
        fontSize=25, font='Courier New')).mark_area(
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='red', offset=0),
                   alt.GradientStop(color='green', offset=1)],
            x1=1,
            x2=1,
            y1=1,
            y2=0,
        ),
    ).encode(
        x=alt.X('year:O', title="Year of exoplanet discovery", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('y:Q', title="Stellar Metallicity (Dex)").stack('zero'),
        tooltip=[alt.Tooltip("y:Q", title="Mean metal content from stars of exoplanet discoveries"),
                 alt.Tooltip("year:Q", title="Year of discovery")]
    ).properties(width=1200, height=400)

    # Color scale to encode metallic content as color (to boost the encoding of position doing it already)
    custom_color_scale = alt.Scale(
        domain=[-0.5, 0.5],
        range=['red', 'green']
    )

    # Legend using a gradient matching the color scheme
    legend = alt.Chart(mean_metallic_content).mark_area(
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='red', offset=0),
                   alt.GradientStop(color='green', offset=1)],
            x1=1,
            x2=1,
            y1=1,
            y2=0,
        ),
    ).encode(
        x=alt.X('year:O', title="Year of exoplanet discovery", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('y:Q', title="Stellar Metallicity (Dex)").stack('zero'),
        color=alt.Color("y:Q", scale=custom_color_scale,
                        legend=alt.Legend(title=wrap("Stellar Metallicity", 11)))
    ).properties(width=1200, height=400)

    return chart + legend


# Plot in row 4 to show that the number of stars increases the mean eccentricity of an exoplanet
def number_of_stars_versus_mean_eccentricity(nasa_exoplanet_archive):
    plot = alt.Chart(nasa_exoplanet_archive, title=alt.TitleParams(
        text=wrap("As the number of stars increases, does the deviation or period of the exoplanet's orbit "
                  "increase?", 52),
        fontSize=15, font='Courier New')).mark_line(point=True).encode(
        x=alt.X('sy_snum:Q', title="Number of stars in the planetary system"),
        y=alt.Y('mean(pl_orbeccen):Q', title="Mean eccentricity (orbital deviation)",
                scale=alt.Scale(domain=[0.15, 0.22])),
        # Encode size as the orbital period
        size=alt.Size("mean(pl_orbper):Q", legend=alt.Legend(title=wrap("Mean orbital period (days)", 13))),
        tooltip=[alt.Tooltip("mean(pl_orbeccen):Q", title="Mean eccentricity"),
                 alt.Tooltip("sy_snum:Q", title="Number of stars in the planetary system"),
                 alt.Tooltip("mean(pl_orbper):Q", title="Mean orbital period")]
    ).properties(width=504, height=350)
    return plot


# Plot in row 4 to show the Goldilocks zone with brightness and temperature for an exoplanet's star
def brightness_versus_temperature_for_host_star(nasa_exoplanet_archive):
    heatmap = alt.Chart(nasa_exoplanet_archive, title=alt.TitleParams(
        text=wrap(
            "Does the universe have a “Goldilocks zone” for the brightness & temperature of an exoplanet's "
            "host star?", 55),
        fontSize=15, font='Courier New')).mark_rect().encode(
        x=alt.X('sy_kmag:Q', bin=alt.Bin(maxbins=60), title="Brightness of the exoplanet's host star"),
        y=alt.Y('st_teff:Q', bin=alt.Bin(maxbins=40), title="Temperature of the exoplanet's host star"),
        color=alt.Color('count():Q', scale=alt.Scale(scheme='greys'), legend=alt.Legend(title=wrap(
            "Exoplanet Discoveries", 11)))).properties(width=504, height=350)
    return heatmap


if __name__ == '__main__':
    # Read the CSV for the Planetary Systems Table from the NASA exoplanet archive
    nasa_exoplanet_archive_csv = gather_exoplanet_attributes("A4_SaiPrathamesh_Dataset.csv")

    # Compute each plot, storing it in a variable that is named after the conclusion from viewing it

    # Row one:
    distance_increasing_over_time = distance_versus_discovery(nasa_exoplanet_archive_csv)
    row_one = alt.hconcat(distance_increasing_over_time)

    # Row two:
    star_brightness_increasing_over_distance = distance_versus_star_brightness(nasa_exoplanet_archive_csv)
    large_range_of_brightness_for_small_number_of_planets_in_planetary_system = (
        range_of_star_brightness_versus_number_of_planets_in_planetary_system(nasa_exoplanet_archive_csv))
    less_planets_in_planetary_system_increases_mass = number_of_planets_in_planetary_system_versus_planet_mass_versus(
        nasa_exoplanet_archive_csv)
    row_two = alt.hconcat(star_brightness_increasing_over_distance,
                          large_range_of_brightness_for_small_number_of_planets_in_planetary_system,
                          less_planets_in_planetary_system_increases_mass,
                          )

    # Row three:
    decrease_in_metal_content_of_suns_of_exoplanets_causes_controversies = (
        average_metal_content_of_star_versus_discovery(nasa_exoplanet_archive_csv))
    row_three = alt.hconcat(decrease_in_metal_content_of_suns_of_exoplanets_causes_controversies)

    # Row four:
    more_stars_in_planetary_system_increases_exoplanet_orbit_deviation = number_of_stars_versus_mean_eccentricity(
        nasa_exoplanet_archive_csv)
    goldilocks_zone_for_brightness_and_temperature_of_host_stars = brightness_versus_temperature_for_host_star(
        nasa_exoplanet_archive_csv)
    row_four = (alt.hconcat(more_stars_in_planetary_system_increases_exoplanet_orbit_deviation,
                            goldilocks_zone_for_brightness_and_temperature_of_host_stars)
                .resolve_scale(size='independent', shape='independent', color='independent'))

    # Plot the overall visualization with all four rows
    Prathamesh_NASA_Exoplanet_Dashboard = (alt.vconcat(row_one, row_two, row_three, row_four,
                                                       title=alt.TitleParams(
                                                           text=wrap(
                                                               "🌔 Prathamesh's NASA Exoplanet Dashboard 🌖", 41),
                                                           subtitle=wrap("Exploring the relationships among "
                                                                         "exoplanets and their stars ‎", 60),
                                                           subtitleFont='Tahoma', subtitleFontSize=30,
                                                           subtitleFontStyle='italic'))
                                           .resolve_scale(size='independent', shape='independent', color='independent')
                                           .configure_axis(labelFontSize=10, titleFontSize=15)
                                           .configure_legend(labelFontSize=13, titleFontSize=15)
                                           .configure_scale(bandPaddingInner=0.2)
                                           .configure_title(font="Tahoma", fontSize=50, anchor='middle',
                                                            align="center"))

    Prathamesh_NASA_Exoplanet_Dashboard.save(fp="A4_SaiPrathamesh_Artefact.html", embed_options={"actions": False})