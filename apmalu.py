'''Calculate area per molecule in any lipid ultrastructure (APMALU).'''

import numpy as np
import scipy

class AreaMolecule(object):
    '''Calculate the area per molecule for any 
    arbitrary lipid ultrastructure. Input includes
    ordered arrays of centroids and heads. The heads
    are for identifying the facet of the 3D Voronoi
    polyhedron that faces in the correct direction,
    and is therefore of interest for surface area calculation.'''

    def __init__(self, centroids, heads):
        self.centroids = centroids
        self.heads = heads

    def molecule_facets(self):
        '''Return the facets of the input molecules, 
        which are to be used for calculating their
        respective surface areas.'''
        vor = scipy.spatial.Voronoi(self.centroids)
        vor_vertices = vor.vertices
        index = 0
        list_head_simplex_coords = [] #for the 'head' simplices I'll eventually want to calculate SA of
        for voronoi_region in vor.regions:
            voronoi_region_vertex_coords = vor_vertices[voronoi_region]
            hull = scipy.spatial.ConvexHull(voronoi_region_vertex_coords)
            simplices = hull.points[hull.simplices]
            #find the centroid of each simplex of the polyhedron
            simplex_centroids = np.array([np.average(simplex, axis = 0) for simplex in simplices])
            #then find the index of the simplex that is closest to the head particle
            target_head_particle = self.heads[index, ...]
            distance_matrix = scipy.spatial.distance.cdist(simplex_centroids, np.reshape(target_head_particle, (1,3)))
            index_closest_simplex = np.argmin(distance_matrix)
            simplex_of_interest = simplices[index_closest_simplex]
            list_head_simplex_coords.append(simplex_of_interest)
        return list_head_simplex_coords
