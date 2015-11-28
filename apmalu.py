'''Calculate area per molecule in any lipid ultrastructure (APMALU).'''

import numpy as np
import scipy.spatial
import cPickle as pickle #debug work

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
        for voronoi_region in vor.regions[:-1]: #for some reason len(vor.regions) = number of generators + 1 -- why?
            print 'index:', index, 'of', self.centroids.shape[0]
            #print 'voronoi_region:', voronoi_region
            #print 'num vertices in voronoi region:', len(voronoi_region)
            #exclude Voronoi vertices outside the diagram (can I safely do this?):
            voronoi_region = np.array(voronoi_region)
            voronoi_region = list(voronoi_region[voronoi_region != -1])
            voronoi_region_vertex_coords = vor_vertices[voronoi_region]
            #print 'voronoi_region_vertex_coords.shape:', voronoi_region_vertex_coords.shape
            try:
                hull = scipy.spatial.ConvexHull(voronoi_region_vertex_coords)
            except: #try iteratively removing the points until ConvexHull works (need to understand this issue better)
                for skip_value in xrange(1,8): #remove up to 7 points
                    try:
                        print 'trying skip_value:', skip_value
                        print 'index:', index
                        hull = scipy.spatial.ConvexHull(voronoi_region_vertex_coords[skip_value:,...])
                    except: 
                        if skip_value < 7:
                            continue
                        else:
                            print 'failed to recover after reaching skip_value', skip_value, 'at index', index
            simplices = hull.points[hull.simplices]
            #find the centroid of each simplex of the polyhedron
            simplex_centroids = np.array([np.average(simplex, axis = 0) for simplex in simplices])
            #then find the index of the simplex that is closest to the head particle
            target_head_particle = self.heads[index, ...]
            distance_matrix = scipy.spatial.distance.cdist(simplex_centroids, np.reshape(target_head_particle, (1,3)))
            index_closest_simplex = np.argmin(distance_matrix)
            simplex_of_interest = simplices[index_closest_simplex]
            list_head_simplex_coords.append(simplex_of_interest)
            index += 1
        return list_head_simplex_coords
