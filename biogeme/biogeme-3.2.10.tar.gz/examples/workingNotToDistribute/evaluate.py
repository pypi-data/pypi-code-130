from biogeme import models
from biogeme.expressions import Beta, defineNumberingOfElementaryExpressions
import biogeme.cexpressions as ee

b1 = Beta('b1', 1, None, None, 0)
b2 = Beta('b2', 1, None, None, 0)

e1 = b1 + b2
e2 = b1 * b2

my_expressions = [e1, e2]

(
    elementaryExpressionIndex,
    allFreeBetas,
    freeBetaNames,
    allFixedBetas,
    fixedBetaNames,
    allRandomVariables,
    randomVariableNames,
    allDraws,
    drawNames,
) = defineNumberingOfElementaryExpressions(
    my_expressions,
    list(),
)

the_ee = ee.pyEvaluateExpression()
the_ee.setExpressions([e1.getSignature(), e2.getSignature()])

