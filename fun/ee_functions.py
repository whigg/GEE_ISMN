
def lc_filter(location_dict):
    """
    description of the function
    """
    lc = ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V/Global").first()
    valid_ids = [20, 30, 40, 60, 100]
    lc_dict = {}

    for name, location in location_dict.items():
        lc_value = lc.select("discrete_classification").reduceRegion(ee.Reducer.first(), location, 10).get(
            "discrete_classification")
        lc_dict[name] = lc_value.getInfo()

    for name, value in lc_dict.items():
        if value not in valid_ids:
            del location_dict[name]

    return location_dict


def get_image_collection(location_dict):
    """
    description of the function
    """
    imagecoll = {}

    ## Set additional filters
    mode = ee.Filter.eq('instrumentMode', 'IW')  # IW = Interferometric Wide Swath
    res = ee.Filter.eq('resolution', 'H')  # H = High

    ## Apply filters to image collection for each location and save results in dictionary
    for name, location in location_dict.items():
        s1 = ee.ImageCollection('COPERNICUS/S1_GRD').filter(mode).filter(res).filterBounds(location)
        s1_desc = s1.filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))
        s1_asc = s1.filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))

        ## Add data to dictionary
        imagecoll[name] = [location, s1_desc, s1_asc]

    ## Convert to dataframe
    # ImageColl = pd.DataFrame(ImageColl)

    return imagecoll


def get_s1_date(out):
    """ Obtains the SAR image acquisition date from the product ID
    Args:
        out (List of dictionaries): Each dictionary corresponds to the sentinel1 info of an image
    Returns:
        Dates : A list of the acquisition dates

    @author: crisj
    modified by: Marco Wolsza
    """
    dates = np.zeros(len(out)).tolist()
    vh = np.zeros(len(out)).tolist()
    vv = np.zeros(len(out)).tolist()
    angle = np.zeros(len(out)).tolist()
    df = pd.DataFrame()
    for i in range(len(out)):
        a = out[i]['id']
        b = a.split(sep='_')
        # b1=b[4].split(sep='T')
        # b2=b1[0]
        b2 = b[4].replace('T', ' ')
        dates[i] = datetime.datetime.strptime(b2, "%Y%m%d %H%M%S")
        vh[i] = out[i]['VH']
        vv[i] = out[i]['VV']
        angle[i] = out[i]['angle']

    df['Dates'] = dates
    df['VH'] = vh
    df['VV'] = vv
    df['angle'] = angle
    df.set_index('Dates', inplace=True)

    return df


def simplify(fc):
    """Take a feature collection, as returned by mapping a reducer to a ImageCollection,
        and reshape it into a simpler list of dictionaries
    Args:
        fc (dict): Dictionary representation of a feature collection, as returned
            by mapping a reducer to an ImageCollection
    Returns:
        list: A list of dictionaries.

    @author: crisj
    """
    def feature2dict(f):
        id = f['id']
        out = f['properties']
        out.update(id=id)
        return out
    out = [feature2dict(x) for x in fc['features']]

    return out


def time_series_of_a_point(img_collection, point):
    """
    @author: crisj
    Modified by: Marco Wolsza
    """
    l = img_collection.filterBounds(point).getRegion(point, 30).getInfo()
    out = [dict(zip(l[0], values)) for values in l[1:]]
    df = get_s1_date(out)
    df = df.sort_index(axis=0)

    return df


def time_series_of_a_region(img_collection, geometry):

    def _reduce_region(image):
        """Spatial aggregation function for a single image and a polygon feature"""
        # The reduction is specified by providing the reducer (ee.Reducer.mean()), the geometry  (a polygon coord),
        # at the scale (30 meters)
        # Feature needs to be rebuilt because the backend doesn't accept to map
        # functions that return dictionaries
        stat_dict = image.reduceRegion(ee.Reducer.mean(), geometry, 30)
        return ee.Feature(None, stat_dict)

    fc = img_collection.filterBounds(geometry).map(_reduce_region).getInfo()
    out = simplify(fc)
    df = get_s1_date(out)
    df = df.sort_index(axis=0)

    return df