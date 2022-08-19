import unittest
import scipy.stats
import numpy as np
from AutoFeedback.randomclass import randomvar as rv


class VarErrorTests(unittest.TestCase):
    def test_integer(self):
        r = rv(expectation=0)
        r.diagnosis = "integer"
        error_message = """The googlyboo should only take integer values
             You should be generating integer valued discrete random variables
             Your random variables should thus only ever take integer values
             """
        assert(error_message == r.get_error("googlyboo"))

    def test_range(self):
        r = rv(expectation=0, vmin=-1, vmax=1)
        r.diagnosis = "range"
        error_message = """The googlyboo fall outside the allowed range of
values for this type of random variable"""
        error_message += """\n The random variable should be between
 -1 and 1"""
        assert(error_message == r.get_error("googlyboo"))

    def test_range_up(self):
        r = rv(expectation=0, vmin=-1)
        r.diagnosis = "range"
        error_message = """The googlyboo fall outside the allowed range of values for this
 type of random variable"""
        error_message += """\n The random variable should be greater
 than or equal to -1"""
        assert(error_message[-1] == r.get_error("googlyboo")[-1])

    def test_range_lo(self):
        r = rv(expectation=0, vmax=-1)
        r.diagnosis = "range"
        error_message = """The googlyboo fall outside the allowed range of values for this
 type of random variable"""
        error_message += """\n The random variable should be less
 than or equal to -1"""
        assert(error_message[-1] == r.get_error("googlyboo")[-1])

    def test_hypo(self):
        r = rv(expectation=0)
        r.diagnosis = "hypothesis"
        error_message = """The googlyboo appear to be
sampled from the wrong distribution

            To test if you generating a random variable from the correct
            distribution the test code performs a hypothesis test.  The null
            hypothesis in this test is that you are sampling from the desired
            distribution and the alternative is that you are not sampling the
            correct distribution.  The size of the critical region is
            determined using a a significance level of 1%.  There is thus a
            small probability that you will fail on this test even if your code
            is correct. If you see this error only you should thus run the
            calculation again to check whether the hypothesis test is giving a
            type I error.  If you fail this test twice your code is most likely
            wrong.
            """
        assert(error_message == r.get_error("googlyboo"))

    def test_number(self):
        r = rv(expectation=0)
        r.diagnosis = "number"
        error_message = """The googlyboo is not generating the correct number
of random variables

            You should be generating a vector that contains multiple random
            variables in this object
            """
        assert(error_message == r.get_error("googlyboo"))

    def test_conf_error(self):
        r = rv(expectation=0)
        r.diagnosis = "conf_number"
        error_message = """The googlyboo is not generating the correct number
of random variables.

            googlyboo should return three random variables.  The first of these
            is the lower bound for the confidence limit.  The second is the
            sample mean and the third is the upper bound for the confidence
            limit
            """
        assert(error_message == r.get_error("googlyboo")) 

    def test_unc_error(self):
        r = rv(expectation=0)
        r.diagnosis = "uncertainty_number"
        error_message = """The googlyboo is not generating the correct number
of random variables.

            googlyboo should return two random variables.  The first of these
            is the sample mean and the second is the width of the error bar
            for the specified confidence interval around the sample mean
            """
        assert(error_message == r.get_error("googlyboo"))  

    def test_length(self):
        r = rv(expectation=0, vmin=0, vmax=1 )
        r2 = rv( expectation=[0,0,0], vmin=[0,0,0], vmax=[1,1,1] )
        message="""normal random variable between 0 and 1 with expectation 0""" 
        assert( message==str(r) and len(r)==1 and len(r2)==3 )

    def test_bernoulli(self):
        r = rv(expectation=0, variance=0.5, vmin=0, vmax=1, isinteger=True)
        assert( r.check_value( 0 ) and r.check_value( 1 ) and not r.check_value( 0.5 ) and not r.check_value(-1) and not r.check_value(2) )

    def test_vmin_only(self):
        r = rv(expectation=0, variance=1, vmin=0 )
        assert( r.check_value( 0 ) and r.check_value( 1 ) and not r.check_value( -1 ) )

    def test_vmax_only(self):
        r = rv(expectation=0, variance=1, vmax=1 )
        assert( r.check_value( -1 ) and r.check_value( 1 ) and not r.check_value( 2 ) )

    def test_multiple_bernoulli(self) :
        r = rv(expectation=0.5, variance=0.25, vmin=0, vmax=1, isinteger=True )
        assert( r.check_value( [0,1,0] ) and not r.check_value( [0,1,2] ) and not r.check_value( [0,1,-1] ) and not r.check_value( [0,1,0.5] ) )

    def test_bernoulli_vector(self):
        r = rv(expectation=[0,0,0], variance=[0.5,0.5,0.5], vmin=[0,0,0], vmax=[1,1,1], isinteger=[True,True,True])
        assert( r.check_value( [0,1,0] ) and not r.check_value( [0,0,0.5] ) and not r.check_value( [0,1,2] ) and not r.check_value( [0,1,-1] ) )

    def test_vector(self):
       r = rv( expectation=[0,0,0], variance=[1,1,1], isinteger=[False,False,False] )
       assert( r.check_value( [0,0,0] ) and not r.check_value( [0] ) )

    def test_single_normal(self):
        r = rv(expectation=0, variance=1)
        assert( r.check_value( scipy.stats.norm.ppf(0.02)) and not r.check_value( scipy.stats.norm.ppf(0.005)) and 
                r.check_value( scipy.stats.norm.ppf(0.98)) and not r.check_value( scipy.stats.norm.ppf(0.998)) )

    def test_correct_multiple_normal(self):
        r = rv( expectation=[0,0,0], variance=[1,1,1], isinteger=[False,False,False] )
        vals1 = [scipy.stats.norm.ppf(0.02),scipy.stats.norm.ppf(0.5),scipy.stats.norm.ppf(0.98)]
        vals2 = [scipy.stats.norm.ppf(0.02),scipy.stats.norm.ppf(0.02),scipy.stats.norm.ppf(0.005)]
        vals3 = [scipy.stats.norm.ppf(0.02),scipy.stats.norm.ppf(0.02),scipy.stats.norm.ppf(0.998)]
        assert( r.check_value( vals1 ) and not r.check_value( vals2 ) and not r.check_value( vals3 ) ) 

    def test_correct_meanconv(self):
        r, vals = rv( expectation=0, variance=1, meanconv=True ), []
        for i in range(1,200) : 
            if np.random.uniform(0,1)<0.5 : vals.append( scipy.stats.norm.ppf( 0.02, loc=0, scale = np.sqrt(1/i) ) )
            else : vals.append( scipy.stats.norm.ppf( 0.98, loc=0, scale = np.sqrt(1/i) ) )
        vals2 = []
        for i in range(1,200) :
            if np.random.uniform(0,1)<0.5 : vals2.append( scipy.stats.norm.ppf( 0.002, loc=0, scale = np.sqrt(1/i) ) )
            else : vals2.append( scipy.stats.norm.ppf( 0.998, loc=0, scale = np.sqrt(1/i) ) )
        assert( r.check_value( vals )  and not r.check_value( vals2 ) ) 

    def test_correct_varconv(self):
        r, vals = rv( expectation=0, variance=1, dist="chi2", meanconv=True ), []
        for i in range(1,200) :
            if np.random.uniform(0,1)<0.5 : vals.append( scipy.stats.chi2.ppf( 0.02, i-1 )/(i-1) ) 
            else : vals.append( scipy.stats.chi2.ppf( 0.98, i-1 )/(i-1) )
        vals2 = []
        for i in range(1,200) :
            if np.random.uniform(0,1)<0.5 : vals2.append( scipy.stats.chi2.ppf( 0.002, i-1 ) )
            else : vals2.append( scipy.stats.chi2.ppf( 0.998, i-1 )/(i-1) )
        assert( r.check_value( vals )  and not r.check_value( vals2 )/(i-1) )

    def test_single_chi2(self):
       r = rv(expectation=0, variance=1, dist="chi2", dof=5)
       assert( r.check_value( scipy.stats.chi2.ppf(0.02, 5)/5) and not r.check_value( scipy.stats.chi2.ppf(0.005, 5)/5) and 
               r.check_value( scipy.stats.chi2.ppf(0.98, 5)/5) and not r.check_value( scipy.stats.chi2.ppf(0.998, 5)/5) )

    def test_multiple_chi2(self):
        r = rv( expectation=[0,0,0], variance=[1,1,1], dist="chi2", dof=10, isinteger=[False,False,False] )
        vals1 = [scipy.stats.chi2.ppf(0.02,10)/10,scipy.stats.chi2.ppf(0.5,10)/10,scipy.stats.chi2.ppf(0.98,10)/10]
        vals2 = [scipy.stats.chi2.ppf(0.02,10)/10,scipy.stats.chi2.ppf(0.02,10)/10,scipy.stats.chi2.ppf(0.005,10)/10]
        vals3 = [scipy.stats.chi2.ppf(0.02,10)/10,scipy.stats.chi2.ppf(0.02,10)/10,scipy.stats.chi2.ppf(0.998,10)/10]
        assert( r.check_value( vals1 ) and not r.check_value( vals2 ) and not r.check_value( vals3 ) )

    def test_single_conf(self):
        r, pref = rv(expectation=0, variance=1, dist="chi2", dof=5, limit=0.5), scipy.stats.norm.ppf(0.75)
        goodvar1, goodvar2 = scipy.stats.chi2.ppf(0.02, 5)/5, scipy.stats.chi2.ppf(0.98, 5)/5
        badvar1, badvar2 = scipy.stats.chi2.ppf(0.005, 5)/5, scipy.stats.chi2.ppf(0.998, 5)/5
        assert( r.check_value( pref*np.sqrt(goodvar1) ) and not r.check_value( pref*np.sqrt(badvar1) ) and
                r.check_value( pref*np.sqrt(goodvar2) ) and not r.check_value( pref*np.sqrt(badvar2) ) )

    def test_conflim(self) :
        r, pref = rv( expectation=0, variance=1, dist="conf_lim", dof=9, limit=0.90 ), scipy.stats.norm.ppf(0.95) 
        goodmean1, goodmean2 = scipy.stats.norm.ppf(0.02), scipy.stats.norm.ppf(0.98)
        badmean1, badmean2 = scipy.stats.norm.ppf(0.005), scipy.stats.norm.ppf(0.998)
        goodvar1, goodvar2 = scipy.stats.chi2.ppf(0.02,9)/9, scipy.stats.chi2.ppf(0.98,9)/9
        badvar1, badvar2 = scipy.stats.chi2.ppf(0.005,9)/9, scipy.stats.chi2.ppf(0.998,9)/9
        assert( r.check_value( [goodmean1-pref*np.sqrt(goodvar1), goodmean1, goodmean1+pref*np.sqrt(goodvar2)] ) and 
                r.check_value( [goodmean2-pref*np.sqrt(goodvar2), goodmean2, goodmean2+pref*np.sqrt(goodvar1)] ) and 
                not r.check_value( [goodmean1-pref*np.sqrt(goodvar1), badmean1, goodmean1+pref*np.sqrt(goodvar2)] ) and 
                not r.check_value( [goodmean2-pref*np.sqrt(goodvar2), badmean2, goodmean2+pref*np.sqrt(goodvar1)] ) and 
                not r.check_value( [goodmean1-pref*np.sqrt(badvar1), goodmean1, goodmean1+pref*np.sqrt(goodvar2)] ) and
                not r.check_value( [goodmean2-pref*np.sqrt(goodvar1), goodmean2, goodmean2+pref*np.sqrt(badvar2)] ) and
                not r.check_value( [goodmean2-pref*np.sqrt(goodvar1), goodmean2] ) )

    def test_uncertainty(self):
        r, pref = rv( expectation=0, variance=1, dist="uncertainty", dof=16, limit=0.80 ), scipy.stats.norm.ppf(0.9)
        goodmean1, goodmean2 = scipy.stats.norm.ppf(0.02), scipy.stats.norm.ppf(0.98)
        badmean1, badmean2 = scipy.stats.norm.ppf(0.005), scipy.stats.norm.ppf(0.998)
        goodvar1, goodvar2 = scipy.stats.chi2.ppf(0.02,16)/16, scipy.stats.chi2.ppf(0.98,16)/16
        badvar1, badvar2 = scipy.stats.chi2.ppf(0.005,16)/16, scipy.stats.chi2.ppf(0.998,16)/16
        assert( r.check_value( [goodmean1, pref*np.sqrt(goodvar1)] ) and
                r.check_value( [goodmean2, pref*np.sqrt(goodvar2)] ) and
                not r.check_value( [badmean1, pref*np.sqrt(goodvar1)] ) and
                not r.check_value( [badmean2, pref*np.sqrt(goodvar2)] ) and
                not r.check_value( [goodmean1, pref*np.sqrt(badvar1)] ) and
                not r.check_value( [goodmean2, pref*np.sqrt(badvar2)] ) and
                not r.check_value( [goodmean1-pref*np.sqrt(goodvar1), goodmean1, goodmean1+pref*np.sqrt(goodvar2)] ) )

