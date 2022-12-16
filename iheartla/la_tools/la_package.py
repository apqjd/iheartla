import copy
from ..la_parser.la_types import *
class GPType(IntEnum):
    # Geometry processing
    Invalid = -1
    FacesOfEdge = 0
    Dihedral = 1
    FaceNormal = 2
    AdjacentVerticesV = 3
    IncidentEdgesV = 4
    IncidentFacesV = 5
    IncidentVerticesE = 6
    IncidentFacesE = 7
    DiamondVerticesE = 8
    IncidentVerticesF = 9
    IncidentEdgesF = 10
    AdjacentFacesF = 11
    BuildVertexVector = 12
    BuildEdgeVector = 13
    BuildFaceVector = 14
    GetVerticesE = 15
    GetVerticesF = 16
    GetEdgesF = 17
    Vertices = 18
    Edges = 19
    Faces = 20
    Tets = 21
    Diamond = 22
    DiamondFacesE = 23
    VectorToVertex = 24
    VectorToEdge = 25
    VectorToFace = 26
    VertexPositions = 27
    FaceMatrix = 28
    # dec
    Star = 100
    Closure = 101
    Link = 102
    Boundary = 103
    IsComplex = 104
    IsPureComplex = 105
    #
    MeshSets = 200
    BoundaryMatrices = 201

class MeshData(object):
    def __init__(self, v=None, e=None, f=None, t=None, la_type=None):
        # track the symbols in this assignment: v,e,f = meshset(T)
        self.v = v
        self.e = e
        self.f = f
        self.t = t
        self.la_type = la_type

    def init_dims(self, dim_list):
        if len(dim_list) >= 3:
            self.v = dim_list[0]
            self.e = dim_list[1]
            self.f = dim_list[2]
        if len(dim_list) > 3:
            self.t = dim_list[3]

# dimension name
VI_SIZE = 'vi_size'
EI_SIZE = 'ei_size'
FI_SIZE = 'fi_size'
TI_SIZE = 'ti_size'
#
MESH_CLASS = 'TriangleMesh'
MESH_HELPER = 'MeshConnectivity'
# MeshHelper function
MeshSets = 'MeshSets'
BoundaryMatrices = 'BoundaryMatrices'
FACES_OF_EDGE = 'faces_of_edge'
DIHEDRAL = 'dihedral'
FACE_NORMAL = 'face_normal'
GET_ADJACENT_VERTICES_V = 'get_adjacent_vertices_v'
GET_INCIDENT_EDGES_V = 'get_incident_edges_v'
GET_INCIDENT_FACES_V = 'get_incident_faces_v'
GET_INCIDENT_VERTICES_E = 'get_incident_vertices_e'
GET_INCIDENT_FACES_E = 'get_incident_faces_e'
GET_DIAMOND_VERTICES_E = 'get_diamond_vertices_e'
GET_DIAMOND_FACES_E = 'get_diamond_faces_e'
GET_INCIDENT_VERTICES_F = 'get_incident_vertices_f'
GET_INCIDENT_EDGES_F = 'get_incident_edges_f'
GET_ADJACENT_FACES_F = 'get_adjacent_faces_f'
VERTICES_TO_VECTOR = 'vertices_to_vector'
EDGES_TO_VECTOR = 'edges_to_vector'
FACES_TO_VECTOR = 'faces_to_vector'
VECTOR_TO_VERTICES = 'vector_to_vertices'
VECTOR_TO_EDGES = 'vector_to_edges'
VECTOR_TO_FACES = 'vector_to_faces'
VERTEX_POSITIONS = 'vertex_positions'
FACE_MATRIX = 'face_matrix'
STAR = 'star'
CLOSURE = 'closure'
LINK = 'link'
BOUNDARY = 'boundary'
IS_COMPLEX = 'is_complex'
IS_PURE_COMPLEX = 'is_pure_complex'
GET_VERTICES_E = 'get_vertices_e'
GET_VERTICES_F = 'get_vertices_f'
GET_EDGES_F = 'get_edges_f'
VERTICES = 'vertices'
EDGES = 'edges'
FACES = 'faces'
TETS = 'tets'
DIAMOND = 'diamond'

VI = 'Vi'
EI = 'Ei'
FI = 'Fi'
NEI = 'nEi'
BM1 = 'bm1'
BM2 = 'bm2'
BM3 = 'bm3'
PACKAGES_FUNC_DICT = {'trigonometry': ['sin', 'asin', 'arcsin', 'cos', 'acos', 'arccos', 'tan', 'atan', 'arctan', 'atan2',
                                  'sinh', 'asinh', 'arsinh', 'cosh', 'acosh', 'arcosh', 'tanh', 'atanh', 'artanh',
                                  'cot', 'sec', 'csc'],
                 'linearalgebra': ['trace', 'tr', 'diag', 'vec', 'det', 'rank', 'null', 'orth', 'inv'],
                 MESH_HELPER: [FACES_OF_EDGE, FACE_NORMAL, DIHEDRAL,
                                 GET_ADJACENT_VERTICES_V, GET_INCIDENT_EDGES_V, GET_INCIDENT_FACES_V,
                                 GET_INCIDENT_VERTICES_E, GET_INCIDENT_FACES_E, GET_DIAMOND_VERTICES_E, GET_DIAMOND_FACES_E,
                                 GET_INCIDENT_VERTICES_F, GET_INCIDENT_EDGES_F, GET_ADJACENT_FACES_F,
                                 VERTICES_TO_VECTOR, EDGES_TO_VECTOR, FACES_TO_VECTOR,
                                 VECTOR_TO_VERTICES, VECTOR_TO_EDGES, VECTOR_TO_FACES, VERTEX_POSITIONS, FACE_MATRIX,
                                 GET_VERTICES_E, GET_EDGES_F, GET_VERTICES_F,
                                 STAR, CLOSURE, LINK, BOUNDARY, IS_COMPLEX, IS_PURE_COMPLEX,
                                 VERTICES, EDGES, FACES, TETS, DIAMOND,
                                 MeshSets, BoundaryMatrices]
                      }
PACKAGES_SYM_DICT = {'trigonometry': ['e'],
                 MESH_HELPER: [EDGES, VI, EI, FI, NEI, BM1, BM2, BM3]}
MESH_HELPER_FUNC_MAPPING = {
MeshSets: GPType.MeshSets,
BoundaryMatrices: GPType.BoundaryMatrices,
FACES_OF_EDGE: GPType.FacesOfEdge,
FACE_NORMAL: GPType.FaceNormal,
DIHEDRAL: GPType.Dihedral,
GET_ADJACENT_VERTICES_V: GPType.AdjacentVerticesV,  #
GET_INCIDENT_EDGES_V: GPType.IncidentEdgesV,  #
GET_INCIDENT_FACES_V: GPType.IncidentFacesV,  #
#
GET_INCIDENT_VERTICES_E: GPType.IncidentVerticesE,
GET_INCIDENT_FACES_E: GPType.IncidentFacesE,
GET_DIAMOND_VERTICES_E: GPType.DiamondVerticesE,
GET_DIAMOND_FACES_E: GPType.DiamondFacesE,
#
GET_INCIDENT_VERTICES_F: GPType.IncidentVerticesF,
GET_INCIDENT_EDGES_F: GPType.IncidentEdgesF,
GET_ADJACENT_FACES_F: GPType.AdjacentFacesF,
#
VERTICES_TO_VECTOR: GPType.BuildVertexVector,
EDGES_TO_VECTOR: GPType.BuildEdgeVector,
FACES_TO_VECTOR: GPType.BuildFaceVector,
#
VECTOR_TO_VERTICES: GPType.VectorToVertex,
VECTOR_TO_EDGES: GPType.VectorToEdge,
VECTOR_TO_FACES: GPType.VectorToFace,
VERTEX_POSITIONS: GPType.VertexPositions,
FACE_MATRIX: GPType.FaceMatrix,
GET_VERTICES_E: GPType.GetVerticesE,
GET_EDGES_F: GPType.GetEdgesF,
GET_VERTICES_F: GPType.GetVerticesF,
STAR: GPType.Star,
CLOSURE: GPType.Closure,
LINK: GPType.Link,
BOUNDARY: GPType.Boundary,
IS_COMPLEX: GPType.IsComplex,
IS_PURE_COMPLEX: GPType.IsPureComplex,
VERTICES: GPType.Vertices,
EDGES: GPType.Edges,
FACES: GPType.Faces,
TETS: GPType.Tets,
DIAMOND:GPType.Diamond,
}
MESH_HELPER_SYM_TYPE = {
MeshSets: make_function_type([MeshType()], [VertexSetType(), EdgeSetType(), FaceSetType()]),
BoundaryMatrices: make_function_type([MeshType()], [MatrixType(), MatrixType()]),
# functions
FACES_OF_EDGE: make_function_type([MeshType(),EdgeType()], [FaceSetType()]),
FACE_NORMAL: make_function_type(),
DIHEDRAL: make_function_type(),
GET_ADJACENT_VERTICES_V: make_function_type([MeshType(),VertexType()], [VertexSetType()]),
GET_INCIDENT_EDGES_V: make_function_type([MeshType(),VertexType()], [EdgeSetType()]),
GET_INCIDENT_FACES_V: make_function_type([MeshType(),VertexType()], [FaceSetType()]),
#
GET_INCIDENT_VERTICES_E: make_function_type([MeshType(),EdgeType()], [VertexSetType()]),
GET_INCIDENT_FACES_E: make_function_type([MeshType(),EdgeType()], [FaceSetType()]),
GET_DIAMOND_VERTICES_E: make_function_type([MeshType(),EdgeType()], [VertexSetType()]),
GET_DIAMOND_FACES_E: make_function_type([MeshType(),EdgeType()], [FaceType(), FaceType()]),
#
GET_INCIDENT_VERTICES_F: make_function_type([MeshType(),FaceType()], [VertexSetType()]),
GET_INCIDENT_EDGES_F: make_function_type([MeshType(),FaceType()], [EdgeSetType()]),
GET_ADJACENT_FACES_F: make_function_type([MeshType(),FaceType()], [FaceSetType()]),
#
VERTICES_TO_VECTOR: make_function_type(),  # must be a valid function type for preprocessing
EDGES_TO_VECTOR: make_function_type(),
FACES_TO_VECTOR: make_function_type(),
#
VECTOR_TO_VERTICES: make_function_type(),
VECTOR_TO_EDGES: make_function_type(),
VECTOR_TO_FACES: make_function_type(),
VERTEX_POSITIONS: make_function_type(),
FACE_MATRIX: make_function_type(),
#
GET_VERTICES_E: make_function_type([MeshType(),EdgeType()], [VertexType(), VertexType()]),
GET_EDGES_F: make_function_type([MeshType(),FaceType()], [EdgeType(), EdgeType(), EdgeType()]),
GET_VERTICES_F: make_function_type([MeshType(),FaceType()], [VertexType(), VertexType(), VertexType()]),
#
STAR: make_function_type([MeshType(),SimplicialSetType()], [SimplicialSetType()]),
CLOSURE: make_function_type([MeshType(),SimplicialSetType()], [SimplicialSetType()]),
LINK: make_function_type([MeshType(),SimplicialSetType()], [SimplicialSetType()]),
BOUNDARY: make_function_type([MeshType(),SimplicialSetType()], [SimplicialSetType()]),
IS_COMPLEX: make_function_type([MeshType(),SimplicialSetType()], [IntType()]),
IS_PURE_COMPLEX: make_function_type([MeshType(),SimplicialSetType()], [IntType()]),
#
VERTICES: make_function_type([MeshType(),SimplicialSetType()], [VertexSetType()]),
EDGES: make_function_type([MeshType(),SimplicialSetType()], [EdgeSetType()]),
FACES: make_function_type([MeshType(),SimplicialSetType()], [FaceSetType()]),
TETS: make_function_type([MeshType(),SimplicialSetType()], [TetSetType()]),
DIAMOND: make_function_type([MeshType(),EdgeType()], [SimplicialSetType()]),
# variables
VI: VertexSetType(),
EI: EdgeSetType(),
FI: FaceSetType(),
NEI: EdgeSetType(),
BM1: None,
BM2: None,
BM3: None
}
# need extra info
MESH_HELPER_DYNAMIC_TYPE_LIST = [BM1, BM2, BM3, VERTICES_TO_VECTOR, EDGES_TO_VECTOR, FACES_TO_VECTOR,
                                   VECTOR_TO_VERTICES, VECTOR_TO_EDGES, VECTOR_TO_FACES, VERTEX_POSITIONS, FACE_MATRIX,
                                   MeshSets, BoundaryMatrices]
def merge_dict(dict1, dict2):
    # key:[value,]
    res = copy.deepcopy(dict1)
    for key, value in dict2.items():
        if key in res:
            res[key] += value
        else:
            res[key] = value
    return res
PACKAGES_DICT = merge_dict(PACKAGES_FUNC_DICT, PACKAGES_SYM_DICT)
CLASS_PACKAGES = [MESH_HELPER]

def get_sym_type_from_pkg(sym, pkg, mesh_type=None):
    ret = LaVarType()
    if pkg == MESH_HELPER:
        if sym in MESH_HELPER_SYM_TYPE:
            if sym in MESH_HELPER_DYNAMIC_TYPE_LIST:
                if mesh_type:
                    if sym == BM1:
                        ret = MatrixType(rows=mesh_type.vi_size, cols=mesh_type.ei_size, sparse=True, element_type=ScalarType(is_int=True))
                    elif sym == BM2:
                        ret = MatrixType(rows=mesh_type.ei_size, cols=mesh_type.fi_size, sparse=True, element_type=ScalarType(is_int=True))
                    elif sym == BM3:
                        ret = MatrixType(rows=mesh_type.fi_size, cols=mesh_type.ti_size, sparse=True, element_type=ScalarType(is_int=True))
                    elif sym == VERTICES_TO_VECTOR:
                        ret = make_function_type([MeshType(),VertexSetType()], [VectorType(rows=mesh_type.vi_size)])
                    elif sym == EDGES_TO_VECTOR:
                        ret = make_function_type([MeshType(),EdgeSetType()], [VectorType(rows=mesh_type.ei_size)])
                    elif sym == FACES_TO_VECTOR:
                        ret = make_function_type([MeshType(),FaceSetType()], [VectorType(rows=mesh_type.fi_size)])
                    elif sym == VECTOR_TO_VERTICES:
                        ret = make_function_type([MeshType(),VectorType(rows=mesh_type.vi_size)], [VertexSetType()])
                    elif sym == VECTOR_TO_EDGES:
                        ret = make_function_type([MeshType(),VectorType(rows=mesh_type.ei_size)], [EdgeSetType()])
                    elif sym == VECTOR_TO_FACES:
                        ret = make_function_type([MeshType(),VectorType(rows=mesh_type.fi_size)], [FaceSetType()])
                    elif sym == VERTEX_POSITIONS:
                        ret = make_function_type([MeshType()], [MatrixType(rows=mesh_type.vi_size, cols=3)])
                    elif sym == FACE_MATRIX:
                        ret = make_function_type([MeshType()], [MatrixType(rows=mesh_type.fi_size, cols=3)])
                    elif sym == MeshSets:
                        ret = make_function_type([MeshType()], [VertexSetType(length=mesh_type.vi_size), EdgeSetType(length=mesh_type.ei_size), FaceSetType(length=mesh_type.fi_size)])
                    elif sym == BoundaryMatrices:
                        ret = make_function_type([MeshType()], [MatrixType(rows=mesh_type.vi_size, cols=mesh_type.ei_size, sparse=True, element_type=ScalarType(is_int=True)),
                                                                MatrixType(rows=mesh_type.ei_size, cols=mesh_type.fi_size, sparse=True, element_type=ScalarType(is_int=True))])
                else:
                    ret = MESH_HELPER_SYM_TYPE[sym]
            else:
                ret = MESH_HELPER_SYM_TYPE[sym]
    return ret