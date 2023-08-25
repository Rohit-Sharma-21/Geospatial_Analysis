from qgis.core import QgsGeometry, QgsPointXY, QgsVectorLayer, QgsFeature

school_layer = QgsProject.instance().mapLayersByName('schools')[0] 
college_layer = QgsProject.instance().mapLayersByName('colleges')[0]
admin_boundary_layer = QgsProject.instance().mapLayersByName('admin_boundaries')[0]

line_layer = QgsVectorLayer("LineString?crs=" + school_layer.crs().toWkt(), "LineLayer", "memory")
line_layer_data = line_layer.dataProvider()

school_college_distances = {}  # Create a dictionary to store college names and distances for each school

# Loop through schools
for school_feature in school_layer.getFeatures():
    school_geom = school_feature.geometry()
    within_colleges = [] 
    within_colleges_geom = []

    for admin_boundary_feature in admin_boundary_layer.getFeatures():
        if admin_boundary_feature.geometry().intersects(school_geom):
            admin_boundary_geom = admin_boundary_feature.geometry()
            
            for college_feature in college_layer.getFeatures():
                college_geom = college_feature.geometry()
                if admin_boundary_geom.contains(college_geom):
                    within_colleges.append(college_feature['osm_id'])
                    within_colleges_geom.append(college_geom)
                    
            if within_colleges_geom:                  # Calculate distances and find the closest college
                closest_college_geom = min(within_colleges_geom, key=lambda p: p.distance(school_geom))
                closest_college_name = within_colleges[within_colleges_geom.index(closest_college_geom)]
                
                school_point = QgsPoint(school_geom.asPoint())     #Converting into QgsPoint object
                college_point = QgsPoint(closest_college_geom.asPoint())

                line_geom = QgsGeometry.fromPolyline([school_point, college_point])      # Creating a line geometry between school and college points
                feature = QgsFeature()
                feature.setGeometry(line_geom)
                line_layer_data.addFeature(feature)
                
                print(f"Closest College: {closest_college_name}, to school: {school_feature['osm_id']}")
            else:
                print("No colleges found within the admin boundary of ", admin_boundary_feature['shapeName'] ,"for school ", school_feature['osm_id'] )
QgsProject.instance().addMapLayer(line_layer)