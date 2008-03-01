
#include <math.h>
#include "Python.h"
#include "structmember.h"
#include "numpy/arrayobject.h"
#include "numpy/ufuncobject.h"

#define SAFE_FROMARRAY_1D(a, type)  \
    ((a) == NULL) ? (a) : PyArray_FROMANY(a, type, 1, 1, NPY_IN_ARRAY)

extern "C" {
    PyMODINIT_FUNC init_speedups(void);
    //static PyObject *scatterplot_gather_points(PyObject *args, PyObject *kwargs);
}


// Given a tuple or list of indices and an array length, returns a new array of
// the given length with value 1 at each indices in the list of indices, and 0
// elsewhere.
// The caller must deallocate the array when they are done.
// If selections is NULL or arrayLen is 0, then a null pointer is returned.
char *create_mirror_mask_array(PyObject *selections, int arrayLen)
{
    if ((selections != NULL) && (arrayLen > 0) && (PySequence_Length(selections) > 0))
    {

        char *mirror = new char[arrayLen];
        memset(mirror, 0, arrayLen);
        int numIndices = PySequence_Length(selections);
        PyObject *tmp;
        for (int i=0; i < numIndices; i++)
        {
            tmp = PyTuple_GetItem(selections, i);
            mirror[PyInt_AsLong(tmp)] = 1;
            Py_XDECREF(tmp);
        }
        return mirror;
    }
    else
    {
        return NULL;
    }
}

/*
 * Scatterplot speedups
 */

static char scatterplot_gather_points_doc[] = \
    "Takes index and value arrays, masks, and optional selection arrays, \n" \
    "and returns the list of points and corresponding selection mask for \n" \
    "those points. \n " \
    "\n" \
    "Parameters\n" \
    "----------\n" \
    "index : float array (1D) \n" \
    "index_low : float or None\n" \
    "   The minimum acceptable value in the index array\n" \
    "index_high : float or None \n" \
    "   The maximum acceptable value in the index array\n" \
    "value : float array (1D) \n" \
    "value_low : float or None\n" \
    "   The minimum acceptable value in the value array\n" \
    "value_high : float or None \n" \
    "   The maximum acceptable value in the value array\n" \
    "\n" \
    "Optional Parameters\n" \
    "-------------------\n" \
    "index_mask : bool or int array (1D) \n" \
    "   A mask that indicates which index points should be used\n" \
    "index_sel : sequence of ints \n" \
    "   A list/tuple/array of indices of selected positions in the index array\n " \
    "index_sel_mask : array of ints or bools\n" \
    "   An mask array with True values indicating which points are selected\n" \
    "value_mask : bool or int array (1D) \n" \
    "   A mask that indicates which value points should be used\n" \
    "value_sel : sequence of ints \n" \
    "   A list/tuple/array of indices of selected positions in the value array\n " \
    "value_sel_mask : array of ints or bools\n" \
    "   An mask array with True values indicating which points are selected\n" \
    "\n" \
    "Returns\n" \
    "-------\n" \
    "points : float array (Nx2) \n " \
    "   The points that match all the masking criteria \n" \
    "sel_mask : bool array (1D) \n " \
    "   Mask indicating which indices in **points** are selected \n" \
    "";

#define DEBUG_SPEEDUP 0

static PyObject *scatterplot_gather_points(PyObject *self, PyObject* args, PyObject* kwargs)
{
    PyObject *index, *index_mask, *index_sel, *index_sel_mask;
    PyObject *value, *value_mask, *value_sel, *value_sel_mask;
    PyObject *tmp;

    index = index_mask = index_sel = index_sel_mask = NULL;
    value = value_mask = value_sel = value_sel_mask = NULL;

    // Stores the points and selection array while we're iterating over the input
    npy_float *points = NULL;
    npy_bool *points_mask = NULL; 

    PyObject *np_points, *np_points_mask, *returnval = NULL;

    double index_low, index_high, value_low, value_high;
    unsigned int numValidPts = 0;
    float x, y;

    int numIndex, numValue;
    char *index_sel_mirror, *value_sel_mirror;
    int numpoints;      // The number of points to iterate over in the input arrays

    static char *keywords[] = {"index", "index_low", "index_high",
                               "value", "value_low", "value_high",
                               "index_mask", "index_sel", "index_sel_mask",
                               "value_mask", "value_sel", "value_sel_mask", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OddOdd|OOOOOO", keywords, 
                &index, &index_low, &index_high,
                &value, &value_low, &value_high,
                &index_mask, &index_sel, &index_sel_mask,
                &value_mask, &value_sel, &value_sel_mask))
        return NULL;

#if DEBUG_SPEEDUP
    printf("Parsed arguments\n");
#endif

    index = PyArray_FROMANY(index, NPY_DOUBLE, 1, 1, NPY_IN_ARRAY);
    if (index == NULL)
        goto cleanup;
    value = PyArray_FROMANY(value, NPY_DOUBLE, 1, 1, NPY_IN_ARRAY);
    if (value == NULL)
        goto cleanup;

#if DEBUG_SPEEDUP
    printf("Got index and value\n");
#endif

    index_mask = SAFE_FROMARRAY_1D(index_mask, NPY_BOOL);
    index_sel = SAFE_FROMARRAY_1D(index_sel, NPY_INT);
    index_sel_mask = SAFE_FROMARRAY_1D(index_sel_mask, NPY_BOOL);

    value_mask = SAFE_FROMARRAY_1D(value_mask, NPY_BOOL);
    value_sel = SAFE_FROMARRAY_1D(value_sel, NPY_INT);
    value_sel_mask = SAFE_FROMARRAY_1D(value_sel_mask, NPY_BOOL);

    numIndex = PyArray_DIM(index, 0);
    numValue = PyArray_DIM(value, 0);

    index_sel_mirror = create_mirror_mask_array(index_sel, numIndex);
    value_sel_mirror = create_mirror_mask_array(value_sel, numValue);

#if DEBUG_SPEEDUP
    if ((index_sel_mirror != NULL) || (value_sel_mirror != NULL))
        printf("Created mirrors\n");
    else
        printf("Created empty mirrors\n");
#endif

    // Determine the total number of points to iterate over in the input arrays
    // based on the shorter of index or value
    numpoints = PySequence_Length(index);
    if (PySequence_Length(value) < numpoints)
        numpoints = PySequence_Length(value);

    // Create a new array for the list of good points and selections into that array
    points = new npy_float[numpoints * 2];

#if DEBUG_SPEEDUP
    printf("Created points array\n");
#endif

    if ((index_sel != NULL) || (index_sel_mask != NULL) || 
        (value_sel != NULL) || (value_sel_mask != NULL))
    {
        points_mask = new npy_bool[numpoints];
#if DEBUG_SPEEDUP
        printf("Created points_mask array\n");
#endif
    }


    // Iterate over the list of x,y positions and check to see if they
    // should be copied into the output list
    for (int i=0; i < numpoints; i++)
    {
        x = *((double *) (PyArray_GETPTR1(index, i)));
        y = *((double *) (PyArray_GETPTR1(value, i)));

        if (((index_mask != NULL) && (*(npy_bool*)PyArray_GETPTR1(index_mask, i) == 0)) || 
            ((value_mask != NULL) && (*(npy_bool*)PyArray_GETPTR1(value_mask, i) == 0)))
            continue;

        if (isnan(x) || isnan(y))
            continue;

        if ((x < index_low) || (x > index_high) ||
            (y < value_low) || (y > value_high))
            continue;

        points[numValidPts * 2] = x;
        points[numValidPts * 2 + 1] = y;

        if (((index_sel_mirror != NULL) && (index_sel_mirror[i] == 1)) ||
            ((value_sel_mirror != NULL) && (value_sel_mirror[i] == 1)) ||
            ((index_sel_mask != NULL) && 
                    (*(npy_bool*)PyArray_GETPTR1(index_sel_mask, i) == 1))  ||
            ((value_sel_mask != NULL) && 
                    (*(npy_bool*)PyArray_GETPTR1(value_sel_mask, i) == 1)))
        {
            points_mask[numValidPts] = 1;
        }
        else if (points_mask != NULL)
        {
            points_mask[numValidPts] = 0;
        }

        numValidPts++;
    }

#if DEBUG_SPEEDUP
    printf("Finished main loop\n");
#endif

    // Copy the valid points into a compact array of the right length
    npy_intp dims[2];
    dims[0] = numValidPts;
    dims[1] = 2;
    np_points = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
    for (int i=0; i < numValidPts; i++)
    {
        *((npy_double*) PyArray_GETPTR2(np_points, i, 0)) = points[i*2];
        *((npy_double*) PyArray_GETPTR2(np_points, i, 1)) = points[i*2 + 1];
    }

    if (points_mask != NULL)
    {
        npy_intp maskdims[1];
        maskdims[0] = numValidPts;
        np_points_mask = PyArray_SimpleNew(1, maskdims, NPY_BOOL);
        for (int i=0; i< numValidPts; i++)
            *(npy_bool*)(PyArray_GETPTR1(np_points_mask, i)) = points_mask[i];
    }
    else
    {
        Py_INCREF(Py_None);
        np_points_mask = Py_None;
    }

#if DEBUG_SPEEDUP
    printf("Compacted array\n");
#endif

    returnval = Py_BuildValue("(OO)", np_points, np_points_mask);

    if (index_sel_mirror != NULL)
        delete[] index_sel_mirror;
    if (value_sel_mirror != NULL)
        delete[] value_sel_mirror;
    if (points != NULL)
        delete[] points;
    if (points_mask != NULL)
        delete[] points_mask;

    Py_DECREF(np_points);
    Py_DECREF(np_points_mask);

#if DEBUG_SPEEDUP
    printf("Built return value and DECREFed\n");
#endif

cleanup:
    Py_XDECREF(index);
    Py_XDECREF(index_mask);
    Py_XDECREF(index_sel);
    Py_XDECREF(index_sel_mask);
    Py_XDECREF(value);
    Py_XDECREF(value_mask);
    Py_XDECREF(value_sel);
    Py_XDECREF(value_sel_mask);

#if DEBUG_SPEEDUP
    printf("About to return\n");
    fflush(stdout);
#endif
    return returnval;
}


static PyMethodDef speedups_methods[] = {
    {"scatterplot_gather_points", (PyCFunction)scatterplot_gather_points, 
         METH_VARARGS | METH_KEYWORDS, 
         scatterplot_gather_points_doc},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC init_speedups(void)
{
    PyObject *module = Py_InitModule3("_speedups", speedups_methods,
                "Fast array range/NaN checking to accelerate plotting");
    if (module == NULL)
        return;

    import_array();
};

