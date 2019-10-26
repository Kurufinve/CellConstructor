#!python

from __future__ import print_function
from __future__ import division

import unittest
import urllib2
import numpy as np
import sys, os

import cellconstructor as CC
import cellconstructor.Structure
import cellconstructor.Phonons

__SPGLIB__ = True
try:
    import spglib
except:
    __SPGLIB__ = False

__ASE__ = True
try:
    import ase
    import ase.visualize
except:
    __ASE__ = False


# This function retrives a testing dynamical matrix from the web
def DownloadDynSnSe():
    """
    DOWNLOAD THE DYN FROM WEB
    =========================

    We use urllib to download from the web a testing dynamical matrix.

    Results
    -------
        dyn : CC.Phonons.Phonons()
            The dynamical matrix for test
    """
    NQ = 3
    for i in range(1,NQ +1):
        # Download from the web the dynamical matrices
        dynfile = urllib2.urlopen("https://raw.githubusercontent.com/mesonepigreco/CellConstructor/master/tests/TestSymmetriesSupercell/SnSe.dyn.2x2x2%d" % i)
        with open("dyn.SnSe.%d" % i,'wb') as output:
            output.write(dynfile.read())

    # Load the dynamical matrices
    dyn = CC.Phonons.Phonons("dyn.SnSe.", NQ)

    # Lets remove the downloaded file
    for i in range(1,NQ +1):
        os.remove("dyn.SnSe.%d" % i)

    return dyn


# This function retrives a testing dynamical matrix from the web
def DownloadDynSky():
    """
    DOWNLOAD THE DYN FROM WEB
    =========================

    We use urllib to download from the web a testing dynamical matrix.

    Results
    -------
        dyn : CC.Phonons.Phonons()
            The dynamical matrix for test
    """
    NQ = 4
    for i in range(1,NQ +1):
        # Download from the web the dynamical matrices
        dynfile = urllib2.urlopen("https://raw.githubusercontent.com/mesonepigreco/CellConstructor/master/tests/TestSymmetriesSupercell/skydyn_%d" %i)
        #dynfile = urllib2.urlopen("https://raw.githubusercontent.com/mesonepigreco/CellConstructor/master/tests/TestSymmetriesSupercell/newsscha_odd%d" % i)
        with open("dyn.Sky.%d" % i,'wb') as output:
            output.write(dynfile.read())

    # Load the dynamical matrices
    dyn = CC.Phonons.Phonons("dyn.Sky.", NQ)

    # Lets remove the downloaded file
    for i in range(1,NQ +1):
        os.remove("dyn.Sky.%d" % i)

    return dyn
    
    

class TestStructureMethods(unittest.TestCase):

    def setUp(self):
        # Prepare the structure for the tests
        struct_ice = CC.Structure.Structure(12)

        struct_ice.atoms = ["O", "H", "H"] * 4
        struct_ice.coords[0, :] = [2.1897386602476634,  1.2676932473237612,  0.4274022656440920]
        struct_ice.coords[1, :] = [2.1897386602476634,  1.2543789748068450 , 1.4310249717986974]
        struct_ice.coords[2, :] = [2.1897386602476634,  0.3101819276910475,  0.1262494311426678]
        struct_ice.coords[3, :] = [4.3794773204953268,  2.5395546109658751,  6.6906885580208124]
        struct_ice.coords[4, :] = [5.1833303728919438,  2.0453283392179049,  7.0329865156648150]
        struct_ice.coords[5, :] = [3.5756242725987106,  2.0453283392179049,  7.0329865156648150]
        struct_ice.coords[6, :] = [4.3794773204953268,  2.5362441767130308,  4.0053346514190915]
        struct_ice.coords[7, :] = [4.3794773204953268,  2.5495584492299472,  5.0089573620736969]
        struct_ice.coords[8, :] = [4.3794773204953268,  3.4937555008457450,  3.7041818169176670]
        struct_ice.coords[9, :] = [2.1897386602476634,  1.2643828130709174,  3.1127561677458120]
        struct_ice.coords[10, :] = [1.3858856123510472,  1.7586090848188873,  3.4550541253898150]
        struct_ice.coords[11, :] = [2.9935917126442799,  1.7586090848188873,  3.4550541253898150]

        struct_ice.has_unit_cell = True
        struct_ice.unit_cell = np.zeros((3, 3), dtype = np.float64)
        struct_ice.unit_cell[0,0] = 4.3794773204953268
        struct_ice.unit_cell[1,0] = 2.1897386602476634
        struct_ice.unit_cell[1,1] = 3.8039374195367919
        struct_ice.unit_cell[2,2] = 7.1558647760499996

        #ase.visualize.view(struct_ice.get_ase_atoms())

        self.struct_ice = struct_ice


        # Get a simple cubic structure
        self.struct_simple_cubic = CC.Structure.Structure(1)
        self.struct_simple_cubic.atoms = ["H"]
        self.struct_simple_cubic.has_unit_cell = True
        self.struct_simple_cubic.unit_cell = np.eye(3)
        self.struct_simple_cubic.masses = {"H": 938}


        # Download the complex dynamical matrices from internet
        self.dynSnSe = DownloadDynSnSe()
        self.dynSky = DownloadDynSky()


        
    def test_generate_supercell(self):

        #ase.visualize.view(self.struct_ice.get_ase_atoms())
        
        #print("Generating supercell...",)
        super_structure = self.struct_ice.generate_supercell((2,2,2))
        #print(" Done.")

        # Test if restricting the correct cell works
        ortho_cell = self.struct_ice.unit_cell.copy()
        ortho_cell[1,:] = 2*ortho_cell[1,:] - ortho_cell[0,:]
        #print("Restricting supercell to convertional one...",)
        super_structure.unit_cell = ortho_cell
        super_structure.fix_coords_in_unit_cell()
        #print(" Done.")

        #print("N atoms in the conventional cell = {}".format(super_structure.N_atoms))
        #print("N atoms in the primitive cell = {}".format(self.struct_ice.N_atoms))
        self.assertEqual(super_structure.N_atoms, self.struct_ice.N_atoms*2)
        
    def test_spglib_symmetries(self):
        self.assertTrue(__SPGLIB__)
        self.assertTrue(__ASE__)

        if __SPGLIB__ and __ASE__:
            spacegroup = spglib.get_spacegroup(self.struct_ice.get_ase_atoms())
            self.assertEqual(spacegroup, "Cmc2_1 (36)")

    def test_qe_get_symmetries(self):
        syms = CC.symmetries.QE_Symmetry(self.struct_ice)
        syms.SetupQPoint()

        self.assertEqual(syms.QE_nsymq, 4)

        # Test on the simple cubic
        qe_sym = CC.symmetries.QE_Symmetry(self.struct_simple_cubic)
        qe_sym.SetupQPoint()

        self.assertEqual(qe_sym.QE_nsymq, 48)

        
    def test_stress_symmetries(self):
        syms = CC.symmetries.QE_Symmetry(self.struct_ice)
        syms.ChangeThreshold(1e-1)
        syms.SetupQPoint()

        random_matrix = np.zeros((3,3), dtype = np.float64)
        random_matrix[:,:] = np.random.uniform(size= (3,3))

        syms.ApplySymmetryToMatrix(random_matrix)

        __epsil__ = 1e-8

        # Test hermitianity
        self.assertTrue(np.sum(np.abs(random_matrix - random_matrix.T)) < __epsil__)
        
        voight_stress = np.zeros(6, dtype = np.float64)
        voight_stress[:3] = np.diag(random_matrix)
        voight_stress[3] = random_matrix[1,2]
        voight_stress[4] = random_matrix[0,2]
        voight_stress[5] = random_matrix[0,1]

        # Test orthorombic
        self.assertTrue(np.sum(np.abs(voight_stress[3:])) < __epsil__)

        
    def test_q_star_with_minus_q(self):
        """
        This subroutine tests the interpolation in a supercell 
        where there is a q point so that
        q != -q + G

        In which there is no inversion symmetry (so -q is not in the star)
        Then we try to both recover the correct q star, symmetrize and
        check the symmetrization in the supercell
        """


        dyn = CC.Phonons.Phonons(self.struct_ice)
        
        # Get a random dynamical matrix
        fc_random = np.complex128(np.random.uniform(size = (3 * self.struct_ice.N_atoms, 3 * self.struct_ice.N_atoms)))
        fc_random += fc_random.T 
        
        
        dyn.dynmats = [fc_random]
        dyn.q_tot = [np.array([0,0,0])]
        dyn.q_stars = [[np.array([0,0,0])]]

        # Perform the symmetrization
        #dyn.Symmetrize()

        # Now perform the interpolation
        SUPERCELL = (1,1,3)
        new_dyn = dyn.Interpolate((1,1,1), SUPERCELL)
        new_dyn.Symmetrize()
        super_dyn = new_dyn.GenerateSupercellDyn(new_dyn.GetSupercell())
        fc1 = super_dyn.dynmats[0].copy()
        new_dyn.SymmetrizeSupercell()
        super_dyn = new_dyn.GenerateSupercellDyn(new_dyn.GetSupercell())
        fc2 = super_dyn.dynmats[0].copy()

        self.assertTrue( np.sqrt(np.sum( (fc1 - fc2)**2)) < 1e-6)


    def test_phonons_supercell(self):
        # Build a supercell dynamical matrix
        supercell_size = (2,2,2)
        nat_sc = np.prod(supercell_size)
        fc_random = np.zeros((3*nat_sc, 3*nat_sc), dtype = np.complex128)
        fc_random[:,:] = np.random.uniform(size = (3*nat_sc, 3*nat_sc))
        CC.symmetries.CustomASR(fc_random)
        back = fc_random.copy()
        CC.symmetries.CustomASR(back)

        __epsil__ = 1e-8
        delta = np.sum( (fc_random - back)**2)
        # Acustic sum rule
        self.assertTrue(delta < __epsil__)

        # Get the irreducible q points
        qe_sym = CC.symmetries.QE_Symmetry(self.struct_simple_cubic)
        qe_sym.SetupQPoint()

        q_irr = qe_sym.GetQIrr(supercell_size)
        self.assertEqual(len(q_irr), 4)

        n_qirr = len(q_irr)
        q_tot = CC.symmetries.GetQGrid(self.struct_simple_cubic.unit_cell, supercell_size)
        
        dynq = CC.Phonons.GetDynQFromFCSupercell(fc_random, np.array(q_tot), self.struct_simple_cubic, self.struct_simple_cubic.generate_supercell(supercell_size))


        dyn = CC.Phonons.Phonons()
        for i in range(nat_sc):
            dyn.dynmats.append(dynq[i, :, :])
            dyn.q_tot.append(q_tot[i])
        

        dyn.structure = self.struct_simple_cubic
        dyn.AdjustQStar()

        dyn.Symmetrize()
        dyn.ForcePositiveDefinite()
        
        new_dyn = dyn.GenerateSupercellDyn(dyn.GetSupercell())
        w, p = new_dyn.DyagDinQ(0)

        dyn.Symmetrize()
        new_dyn = dyn.GenerateSupercellDyn(dyn.GetSupercell())
        w_new, p = new_dyn.DyagDinQ(0)

        delta = np.sum( (w[3:] - w_new[3:])**2)
        self.assertTrue(delta < __epsil__)

    def test_polarization_vectors_supercell(self):
        # Download the dynamical matrix from internet
        dyn = DownloadDynSnSe()
        
        dyn.Symmetrize()

        # Get the dynamical matrix in the supercell
        super_dyn = dyn.GenerateSupercellDyn(dyn.GetSupercell())

        # Get the polarization vectors in the supercell without generating the big matrix
        w, pols = dyn.DiagonalizeSupercell()

        # Get the masses
        m = np.tile(super_dyn.structure.get_masses_array(), (3, 1)).T.ravel()

        # Get the polarization vectors times the masses
        new_v = np.einsum("ab, a-> ab", pols, np.sqrt(m))

        # Generate the supercell dyn from the polarization vectors
        sup_dyn = np.einsum("i, ai, bi->ab", w**2, new_v, new_v)

        # Compare the two dynamical matrices
        __tollerance__ = 1e-6

        # Print the scalar product between the polarization vectors
        n_modes = len(w)
        s_mat = pols.T.dot(pols)
        delta_mat = s_mat - np.eye(n_modes)
        #np.savetxt("s_mat.dat", s_mat)
        self.assertTrue( np.sum(delta_mat**2) < __tollerance__)


        delta = np.sum(np.abs(super_dyn.dynmats[0] - sup_dyn)) 

        #print("DELTA:", delta)

        self.assertTrue( delta < __tollerance__)

    def test_dyn_realspace_and_back(self):
        """
        Test in which we take a particularly odd dynamical matrix
        and we generate the dynamical matrix in realspace, and then we 
        return back in q space. The two must match.
        """

        dyn = self.dynSky.Copy()
        superdyn = dyn.GenerateSupercellDyn(dyn.GetSupercell())

        dynq = CC.Phonons.GetDynQFromFCSupercell(superdyn.dynmats[0], np.array(dyn.q_tot), \
            dyn.structure, superdyn.structure)
        
        for iq, q in enumerate(dyn.q_tot):
            delta = dynq[iq,:,:] - dyn.dynmats[iq]
            delta = np.sqrt(np.sum(np.abs(delta)**2))
            self.assertAlmostEqual(delta, 0)

    def test_upsilon_matrix(self):
        """
        In this test we compute the upsilon matrix (inverse phonon covariance) 
        in the supercell both by generating the supercell 
        and by computing upsilon using the DiagonalizeSupercell method.
        These two ways shold give the same result.
        """

        # Get the dynamical matrix
        dyn = self.dynSnSe.Copy()
        T = 300 # K

        # Generate the supercell dynamical matrix
        super_dyn = dyn.GenerateSupercellDyn(dyn.GetSupercell())

        # Compute Upsilon in both ways
        ups_from_supercell = super_dyn.GetUpsilonMatrix(T)
        ups_from_dyn = dyn.GetUpsilonMatrix(T)

        # Perform the comparison
        delta = np.sqrt(np.sum( (ups_from_supercell - ups_from_dyn)**2))
        self.assertAlmostEqual(delta, 0, delta = 1e-5)
        

    def test_symmetries_realspace_supercell(self):
        # Download from internet
        #NQ = 3
        dyn = self.dynSnSe.Copy()

        # Lets add a small random noise at gamma
        for iq, q in enumerate(dyn.q_tot):
            dyn.dynmats[iq][:,:] += np.random.uniform( size = np.shape(dyn.dynmats[0]))


        # Generate the dynamical matrix from the supercell
        dyn_supercell = dyn.GenerateSupercellDyn(dyn.GetSupercell())

        # Get the symmetries in the supercell using SPGLIB
        spg_sym = CC.symmetries.QE_Symmetry(dyn_supercell.structure)
        spg_sym.SetupFromSPGLIB()

        # Perform the symmetrization
        spg_sym.ApplySymmetriesToV2(dyn_supercell.dynmats[0])

        # Apply the custom sum rule
        dyn_supercell.ApplySumRule()

        # Convert back to the original dynamical matrix
        fcq = CC.Phonons.GetDynQFromFCSupercell(dyn_supercell.dynmats[0], np.array(dyn.q_tot), \
            dyn.structure, dyn_supercell.structure)

        # Create the symmetrized dynamical matrix
        new_dyn = dyn.Copy()
        for iq, q in enumerate(dyn.q_tot):
            new_dyn.dynmats[iq] = fcq[iq, :, :]
        
        # Symmetrize using the standard tools
        dyn.Symmetrize()

        threshold = 1e-3

        # Now compare the spectrum between the two matrices
        for iq,q in enumerate(dyn.q_tot):
            w_spglib, dumb = new_dyn.DyagDinQ(iq)
            w_standard, dumb = dyn.DyagDinQ(iq)

            w_spglib *= CC.Units.RY_TO_CM
            w_standard *= CC.Units.RY_TO_CM

            self.assertTrue(np.max(np.abs(w_spglib - w_standard)) < threshold)

        # Lets try to see if the spglib symmetrization correctly symemtrizes also a vector
        random_vector = np.zeros(np.shape(dyn.structure.coords), dtype = np.double)
        random_vector[:,:] = np.random.uniform( size = np.shape(random_vector))

        rv2 = random_vector.copy()

        # Get the symmetries in the unit cell using spglib
        qe_sym = CC.symmetries.QE_Symmetry(dyn.structure)
        qe_sym.SetupFromSPGLIB()
        qe_sym.SymmetrizeVector(random_vector)

        # Get the symmetries using quantum espresso
        qe_sym.SetupQPoint()
        qe_sym.SymmetrizeVector(rv2)

        # Check if rv2 is equal to random_vector
        self.assertTrue( np.sum( (random_vector - rv2)**2) < 1e-8)

    def test_multiple_spglib_symmetries(self):
        """
        This test tries to apply many times the symmetrization.
        If after two application the dynamical matrix changes, 
        there is a problem in the symmetrization.
        """
        dyn = DownloadDynSky()

        dyn.SymmetrizeSupercell()

        new_dyn = dyn.Copy()

        new_dyn.SymmetrizeSupercell()

        for iq, q in enumerate(dyn.q_tot):
            delta = dyn.dynmats[iq] - new_dyn.dynmats[iq]
            delta = np.sqrt(np.sum(np.abs(delta)**2))
            #print("Testing iq = {}, q = {}".format(i, iq))
            self.assertAlmostEqual(delta, 0)
        


    def test_spglib_phonon_symmetries(self):
        # Get the Sky dyn
        # This is a phonon matrix that gave a lot of problem
        # In the symmetrization in the supercell
        dyn = self.dynSky.Copy()

        # Symmetrize using quantum espresso
        dyn_qe = dyn.Copy()
        dyn_qe.Symmetrize()

        # Symmetrize using spblig
        dyn_spglib = dyn.Copy()
        dyn_spglib.SymmetrizeSupercell()
        #__thr__ = 1e-8

        #dyn_qe.save_qe("trial_qe")
        #dyn_spglib.save_qe("trial_spglib")

        # Compare
        for i, iq in enumerate(dyn.q_tot):
            delta = dyn_qe.dynmats[i] - dyn_spglib.dynmats[i]
            delta = np.sqrt(np.sum(np.abs(delta)**2))
            #print("Testing iq = {}, q = {}".format(i, iq))
            self.assertAlmostEqual(delta, 0)
        
        




        



# Run all the tests
suite = unittest.TestLoader().loadTestsFromTestCase(TestStructureMethods)
unittest.TextTestRunner(verbosity=2).run(suite)
