import maya.api.OpenMaya as om

def getDependNode(name):
    try:
        selection_list = om.MSelectionList()
        selection_list.add(name)
        return selection_list.getDependNode(0)
    except:
        om.MGlobal.displayError('No object matches or more than one object matches name: {0}'.format(name))

def getDagPath(name):
    try:
        selection_list = om.MSelectionList()
        selection_list.add(name)
        return selection_list.getDagPath(0)
    except:
        om.MGlobal.displayError('No object matches or more than one object matches name: {0}'.format(name))

def getDagPathNode(name):
    try:
        selection_list = om.MSelectionList()
        selection_list.add(name)
        dag, mObject = selection_list.getComponent(0)
        return dag, mObject
    except:
        om.MGlobal.displayError('No object matches or more than one object matches name: {0}'.format(name))

def getPlug(node, attribute):
    obj = getDagPath(node)
    if obj.hasFn(om.MFn.kTransform):
        transform_fn = om.MFnTransform(obj)
        plug = transform_fn.findPlug(attribute, False)

        return plug

def getAttr(node, attribute):
    plug = getPlug(node, attribute)
    if plug.isCompound:
        numChildren = plug.numChildren()
        value = []
        for i in range(numChildren):
            child_plug = plug.child(i)
            value.append(child_plug.asDouble())
        return value
    else:
        return plug.asDouble()

def setAttr(node, attribute, value):
    plug = getPlug(node, attribute)
    if plug.isCompound:
        for x, val in enumerate(value):
            child_plug = plug.child(x)
            child_plug.setDouble(val)
    else:
        plug.setDouble(value)

def transformGetTranslation(node):
    loc_dag, loc_obj = getDagPathNode(node)
    loc_fn = om.MFnTransform(loc_dag)
    pos = om.MPoint(loc_fn.translation(om.MSpace.kWorld))
    return pos

def transformSetTranslation(node, value):
    obj = getDagPath(node)
    if obj.hasFn(om.MFn.kTransform):
        tranform_fn = om.MFnTransform(obj)

        translation = tranform_fn.translation(om.MSpace.kTransform)
        for x, val in enumerate(value):
            translation[x] = val
        tranform_fn.setTranslation(translation, om.MSpace.kTransform)


def getClosestVertex(mesh, pos, select=True):
    mesh_dag, mesh_obj = getDagPathNode(mesh)
    mesh_fn = om.MFnMesh(mesh_dag)

    closest_point, id = mesh_fn.getClosestPoint(pos, om.MSpace.kWorld)
    mesh_vtx = mesh_fn.getPolygonVertices(id)
    closest_id = mesh_vtx[0]
    closest_dist = mesh_fn.getPoint(mesh_vtx[0]).distanceTo(pos)
    for vtx_id in mesh_vtx[1:]:
        vtx_pos = mesh_fn.getPoint(vtx_id)
        dist = vtx_pos.distanceTo(pos)
        if dist < closest_dist:
            closest_dist = dist
            closest_id = vtx_id

    mfn_components = om.MFnSingleIndexedComponent(mesh_obj)
    mfn_object = mfn_components.create(om.MFn.kMeshVertComponent)
    mfn_components.addElements([closest_id])
    if select:
        selection_list = om.MSelectionList()
        selection_list.add((mesh_dag, mfn_object))
        om.MGlobal.setActiveSelectionList(selection_list)

    return mfn_components, mfn_components.element(0)

