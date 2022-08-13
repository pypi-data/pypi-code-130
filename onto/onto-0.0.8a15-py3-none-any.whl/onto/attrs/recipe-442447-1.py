"""
Ref: http://code.activestate.com/recipes/442447/

META:LICENSE=PSF

OpenSource under PSF and http://creativecommons.org/licenses/by-sa/3.0/
Downloaded as a snippet from activestate.com

http://code.activestate.com/help/terms/

Attribution-ShareAlike 3.0 Unported

CREATIVE COMMONS CORPORATION IS NOT A LAW FIRM AND DOES NOT PROVIDE LEGAL SERVICES. DISTRIBUTION OF THIS LICENSE DOES NOT CREATE AN ATTORNEY-CLIENT RELATIONSHIP. CREATIVE COMMONS PROVIDES THIS INFORMATION ON AN "AS-IS" BASIS. CREATIVE COMMONS MAKES NO WARRANTIES REGARDING THE INFORMATION PROVIDED, AND DISCLAIMS LIABILITY FOR DAMAGES RESULTING FROM ITS USE.
License

THE WORK (AS DEFINED BELOW) IS PROVIDED UNDER THE TERMS OF THIS CREATIVE COMMONS PUBLIC LICENSE ("CCPL" OR "LICENSE"). THE WORK IS PROTECTED BY COPYRIGHT AND/OR OTHER APPLICABLE LAW. ANY USE OF THE WORK OTHER THAN AS AUTHORIZED UNDER THIS LICENSE OR COPYRIGHT LAW IS PROHIBITED.

BY EXERCISING ANY RIGHTS TO THE WORK PROVIDED HERE, YOU ACCEPT AND AGREE TO BE BOUND BY THE TERMS OF THIS LICENSE. TO THE EXTENT THIS LICENSE MAY BE CONSIDERED TO BE A CONTRACT, THE LICENSOR GRANTS YOU THE RIGHTS CONTAINED HERE IN CONSIDERATION OF YOUR ACCEPTANCE OF SUCH TERMS AND CONDITIONS.

1. Definitions

"Adaptation" means a work based upon the Work, or upon the Work and other pre-existing works, such as a translation, adaptation, derivative work, arrangement of music or other alterations of a literary or artistic work, or phonogram or performance and includes cinematographic adaptations or any other form in which the Work may be recast, transformed, or adapted including in any form recognizably derived from the original, except that a work that constitutes a Collection will not be considered an Adaptation for the purpose of this License. For the avoidance of doubt, where the Work is a musical work, performance or phonogram, the synchronization of the Work in timed-relation with a moving image ("synching") will be considered an Adaptation for the purpose of this License.
"Collection" means a collection of literary or artistic works, such as encyclopedias and anthologies, or performances, phonograms or broadcasts, or other works or subject matter other than works listed in Section 1(f) below, which, by reason of the selection and arrangement of their contents, constitute intellectual creations, in which the Work is included in its entirety in unmodified form along with one or more other contributions, each constituting separate and independent works in themselves, which together are assembled into a collective whole. A work that constitutes a Collection will not be considered an Adaptation (as defined below) for the purposes of this License.
"Creative Commons Compatible License" means a license that is listed at https://creativecommons.org/compatiblelicenses that has been approved by Creative Commons as being essentially equivalent to this License, including, at a minimum, because that license: (i) contains terms that have the same purpose, meaning and effect as the License Elements of this License; and, (ii) explicitly permits the relicensing of adaptations of works made available under that license under this License or a Creative Commons jurisdiction license with the same License Elements as this License.
"Distribute" means to make available to the public the original and copies of the Work or Adaptation, as appropriate, through sale or other transfer of ownership.
"License Elements" means the following high-level license attributes as selected by Licensor and indicated in the title of this License: Attribution, ShareAlike.
"Licensor" means the individual, individuals, entity or entities that offer(s) the Work under the terms of this License.
"Original Author" means, in the case of a literary or artistic work, the individual, individuals, entity or entities who created the Work or if no individual or entity can be identified, the publisher; and in addition (i) in the case of a performance the actors, singers, musicians, dancers, and other persons who act, sing, deliver, declaim, play in, interpret or otherwise perform literary or artistic works or expressions of folklore; (ii) in the case of a phonogram the producer being the person or legal entity who first fixes the sounds of a performance or other sounds; and, (iii) in the case of broadcasts, the organization that transmits the broadcast.
"Work" means the literary and/or artistic work offered under the terms of this License including without limitation any production in the literary, scientific and artistic domain, whatever may be the mode or form of its expression including digital form, such as a book, pamphlet and other writing; a lecture, address, sermon or other work of the same nature; a dramatic or dramatico-musical work; a choreographic work or entertainment in dumb show; a musical composition with or without words; a cinematographic work to which are assimilated works expressed by a process analogous to cinematography; a work of drawing, painting, architecture, sculpture, engraving or lithography; a photographic work to which are assimilated works expressed by a process analogous to photography; a work of applied art; an illustration, map, plan, sketch or three-dimensional work relative to geography, topography, architecture or science; a performance; a broadcast; a phonogram; a compilation of data to the extent it is protected as a copyrightable work; or a work performed by a variety or circus performer to the extent it is not otherwise considered a literary or artistic work.
"You" means an individual or entity exercising rights under this License who has not previously violated the terms of this License with respect to the Work, or who has received express permission from the Licensor to exercise rights under this License despite a previous violation.
"Publicly Perform" means to perform public recitations of the Work and to communicate to the public those public recitations, by any means or process, including by wire or wireless means or public digital performances; to make available to the public Works in such a way that members of the public may access these Works from a place and at a place individually chosen by them; to perform the Work to the public by any means or process and the communication to the public of the performances of the Work, including by public digital performance; to broadcast and rebroadcast the Work by any means including signs, sounds or images.
"Reproduce" means to make copies of the Work by any means including without limitation by sound or visual recordings and the right of fixation and reproducing fixations of the Work, including storage of a protected performance or phonogram in digital form or other electronic medium.
2. Fair Dealing Rights. Nothing in this License is intended to reduce, limit, or restrict any uses free from copyright or rights arising from limitations or exceptions that are provided for in connection with the copyright protection under copyright law or other applicable laws.

3. License Grant. Subject to the terms and conditions of this License, Licensor hereby grants You a worldwide, royalty-free, non-exclusive, perpetual (for the duration of the applicable copyright) license to exercise the rights in the Work as stated below:

to Reproduce the Work, to incorporate the Work into one or more Collections, and to Reproduce the Work as incorporated in the Collections;
to create and Reproduce Adaptations provided that any such Adaptation, including any translation in any medium, takes reasonable steps to clearly label, demarcate or otherwise identify that changes were made to the original Work. For example, a translation could be marked "The original work was translated from English to Spanish," or a modification could indicate "The original work has been modified.";
to Distribute and Publicly Perform the Work including as incorporated in Collections; and,
to Distribute and Publicly Perform Adaptations.
For the avoidance of doubt:

Non-waivable Compulsory License Schemes. In those jurisdictions in which the right to collect royalties through any statutory or compulsory licensing scheme cannot be waived, the Licensor reserves the exclusive right to collect such royalties for any exercise by You of the rights granted under this License;
Waivable Compulsory License Schemes. In those jurisdictions in which the right to collect royalties through any statutory or compulsory licensing scheme can be waived, the Licensor waives the exclusive right to collect such royalties for any exercise by You of the rights granted under this License; and,
Voluntary License Schemes. The Licensor waives the right to collect royalties, whether individually or, in the event that the Licensor is a member of a collecting society that administers voluntary licensing schemes, via that society, from any exercise by You of the rights granted under this License.
The above rights may be exercised in all media and formats whether now known or hereafter devised. The above rights include the right to make such modifications as are technically necessary to exercise the rights in other media and formats. Subject to Section 8(f), all rights not expressly granted by Licensor are hereby reserved.

4. Restrictions. The license granted in Section 3 above is expressly made subject to and limited by the following restrictions:

You may Distribute or Publicly Perform the Work only under the terms of this License. You must include a copy of, or the Uniform Resource Identifier (URI) for, this License with every copy of the Work You Distribute or Publicly Perform. You may not offer or impose any terms on the Work that restrict the terms of this License or the ability of the recipient of the Work to exercise the rights granted to that recipient under the terms of the License. You may not sublicense the Work. You must keep intact all notices that refer to this License and to the disclaimer of warranties with every copy of the Work You Distribute or Publicly Perform. When You Distribute or Publicly Perform the Work, You may not impose any effective technological measures on the Work that restrict the ability of a recipient of the Work from You to exercise the rights granted to that recipient under the terms of the License. This Section 4(a) applies to the Work as incorporated in a Collection, but this does not require the Collection apart from the Work itself to be made subject to the terms of this License. If You create a Collection, upon notice from any Licensor You must, to the extent practicable, remove from the Collection any credit as required by Section 4(c), as requested. If You create an Adaptation, upon notice from any Licensor You must, to the extent practicable, remove from the Adaptation any credit as required by Section 4(c), as requested.
You may Distribute or Publicly Perform an Adaptation only under the terms of: (i) this License; (ii) a later version of this License with the same License Elements as this License; (iii) a Creative Commons jurisdiction license (either this or a later license version) that contains the same License Elements as this License (e.g., Attribution-ShareAlike 3.0 US)); (iv) a Creative Commons Compatible License. If you license the Adaptation under one of the licenses mentioned in (iv), you must comply with the terms of that license. If you license the Adaptation under the terms of any of the licenses mentioned in (i), (ii) or (iii) (the "Applicable License"), you must comply with the terms of the Applicable License generally and the following provisions: (I) You must include a copy of, or the URI for, the Applicable License with every copy of each Adaptation You Distribute or Publicly Perform; (II) You may not offer or impose any terms on the Adaptation that restrict the terms of the Applicable License or the ability of the recipient of the Adaptation to exercise the rights granted to that recipient under the terms of the Applicable License; (III) You must keep intact all notices that refer to the Applicable License and to the disclaimer of warranties with every copy of the Work as included in the Adaptation You Distribute or Publicly Perform; (IV) when You Distribute or Publicly Perform the Adaptation, You may not impose any effective technological measures on the Adaptation that restrict the ability of a recipient of the Adaptation from You to exercise the rights granted to that recipient under the terms of the Applicable License. This Section 4(b) applies to the Adaptation as incorporated in a Collection, but this does not require the Collection apart from the Adaptation itself to be made subject to the terms of the Applicable License.
If You Distribute, or Publicly Perform the Work or any Adaptations or Collections, You must, unless a request has been made pursuant to Section 4(a), keep intact all copyright notices for the Work and provide, reasonable to the medium or means You are utilizing: (i) the name of the Original Author (or pseudonym, if applicable) if supplied, and/or if the Original Author and/or Licensor designate another party or parties (e.g., a sponsor institute, publishing entity, journal) for attribution ("Attribution Parties") in Licensor's copyright notice, terms of service or by other reasonable means, the name of such party or parties; (ii) the title of the Work if supplied; (iii) to the extent reasonably practicable, the URI, if any, that Licensor specifies to be associated with the Work, unless such URI does not refer to the copyright notice or licensing information for the Work; and (iv) , consistent with Ssection 3(b), in the case of an Adaptation, a credit identifying the use of the Work in the Adaptation (e.g., "French translation of the Work by Original Author," or "Screenplay based on original Work by Original Author"). The credit required by this Section 4(c) may be implemented in any reasonable manner; provided, however, that in the case of a Adaptation or Collection, at a minimum such credit will appear, if a credit for all contributing authors of the Adaptation or Collection appears, then as part of these credits and in a manner at least as prominent as the credits for the other contributing authors. For the avoidance of doubt, You may only use the credit required by this Section for the purpose of attribution in the manner set out above and, by exercising Your rights under this License, You may not implicitly or explicitly assert or imply any connection with, sponsorship or endorsement by the Original Author, Licensor and/or Attribution Parties, as appropriate, of You or Your use of the Work, without the separate, express prior written permission of the Original Author, Licensor and/or Attribution Parties.
Except as otherwise agreed in writing by the Licensor or as may be otherwise permitted by applicable law, if You Reproduce, Distribute or Publicly Perform the Work either by itself or as part of any Adaptations or Collections, You must not distort, mutilate, modify or take other derogatory action in relation to the Work which would be prejudicial to the Original Author's honor or reputation. Licensor agrees that in those jurisdictions (e.g. Japan), in which any exercise of the right granted in Section 3(b) of this License (the right to make Adaptations) would be deemed to be a distortion, mutilation, modification or other derogatory action prejudicial to the Original Author's honor and reputation, the Licensor will waive or not assert, as appropriate, this Section, to the fullest extent permitted by the applicable national law, to enable You to reasonably exercise Your right under Section 3(b) of this License (right to make Adaptations) but not otherwise.
5. Representations, Warranties and Disclaimer

UNLESS OTHERWISE MUTUALLY AGREED TO BY THE PARTIES IN WRITING, LICENSOR OFFERS THE WORK AS-IS AND MAKES NO REPRESENTATIONS OR WARRANTIES OF ANY KIND CONCERNING THE WORK, EXPRESS, IMPLIED, STATUTORY OR OTHERWISE, INCLUDING, WITHOUT LIMITATION, WARRANTIES OF TITLE, MERCHANTIBILITY, FITNESS FOR A PARTICULAR PURPOSE, NONINFRINGEMENT, OR THE ABSENCE OF LATENT OR OTHER DEFECTS, ACCURACY, OR THE PRESENCE OF ABSENCE OF ERRORS, WHETHER OR NOT DISCOVERABLE. SOME JURISDICTIONS DO NOT ALLOW THE EXCLUSION OF IMPLIED WARRANTIES, SO SUCH EXCLUSION MAY NOT APPLY TO YOU.

6. Limitation on Liability. EXCEPT TO THE EXTENT REQUIRED BY APPLICABLE LAW, IN NO EVENT WILL LICENSOR BE LIABLE TO YOU ON ANY LEGAL THEORY FOR ANY SPECIAL, INCIDENTAL, CONSEQUENTIAL, PUNITIVE OR EXEMPLARY DAMAGES ARISING OUT OF THIS LICENSE OR THE USE OF THE WORK, EVEN IF LICENSOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

7. Termination

This License and the rights granted hereunder will terminate automatically upon any breach by You of the terms of this License. Individuals or entities who have received Adaptations or Collections from You under this License, however, will not have their licenses terminated provided such individuals or entities remain in full compliance with those licenses. Sections 1, 2, 5, 6, 7, and 8 will survive any termination of this License.
Subject to the above terms and conditions, the license granted here is perpetual (for the duration of the applicable copyright in the Work). Notwithstanding the above, Licensor reserves the right to release the Work under different license terms or to stop distributing the Work at any time; provided, however that any such election will not serve to withdraw this License (or any other license that has been, or is required to be, granted under the terms of this License), and this License will continue in full force and effect unless terminated as stated above.
8. Miscellaneous

Each time You Distribute or Publicly Perform the Work or a Collection, the Licensor offers to the recipient a license to the Work on the same terms and conditions as the license granted to You under this License.
Each time You Distribute or Publicly Perform an Adaptation, Licensor offers to the recipient a license to the original Work on the same terms and conditions as the license granted to You under this License.
If any provision of this License is invalid or unenforceable under applicable law, it shall not affect the validity or enforceability of the remainder of the terms of this License, and without further action by the parties to this agreement, such provision shall be reformed to the minimum extent necessary to make such provision valid and enforceable.
No term or provision of this License shall be deemed waived and no breach consented to unless such waiver or consent shall be in writing and signed by the party to be charged with such waiver or consent.
This License constitutes the entire agreement between the parties with respect to the Work licensed here. There are no understandings, agreements or representations with respect to the Work not specified here. Licensor shall not be bound by any additional provisions that may appear in any communication from You. This License may not be modified without the mutual written agreement of the Licensor and You.
The rights granted under, and the subject matter referenced, in this License were drafted utilizing the terminology of the Berne Convention for the Protection of Literary and Artistic Works (as amended on September 28, 1979), the Rome Convention of 1961, the WIPO Copyright Treaty of 1996, the WIPO Performances and Phonograms Treaty of 1996 and the Universal Copyright Convention (as revised on July 24, 1971). These rights and subject matter take effect in the relevant jurisdiction in which the License terms are sought to be enforced according to the corresponding provisions of the implementation of those treaty provisions in the applicable national law. If the standard suite of rights granted under applicable copyright law includes additional rights not granted under this License, such additional rights are deemed to be included in the License; this License is not intended to restrict the license of any rights under applicable law.
Creative Commons Notice

Creative Commons is not a party to this License, and makes no warranty whatsoever in connection with the Work. Creative Commons will not be liable to You or any party on any legal theory for any damages whatsoever, including without limitation any general, special, incidental or consequential damages arising in connection to this license. Notwithstanding the foregoing two (2) sentences, if Creative Commons has expressly identified itself as the Licensor hereunder, it shall have all rights and obligations of Licensor.

Except for the limited purpose of indicating to the public that the Work is licensed under the CCPL, Creative Commons does not authorize the use by either party of the trademark "Creative Commons" or any related trademark or logo of Creative Commons without the prior written consent of Creative Commons. Any permitted use will be in compliance with Creative Commons' then-current trademark usage guidelines, as may be published on its website or otherwise made available upon request from time to time. For the avoidance of doubt, this trademark restriction does not form part of the License.

Creative Commons may be contacted at https://creativecommons.org/.

"""


"""A wrapper around DBAPI-compliant databases to support iteration
and generator expression syntax for requests, instead of SQL

To get an iterator, initialize a connection to the database, then
set the cursor attribute of the query class to its cursor

Create an instance of Table for the tables you want to use

Then you can use the class query. You create an instance by passing
a generator expression as parameter. This instance translates the
generator expression in an SQL statement ; then you can iterate
on it to get the selected items as objects, dictionaries or lists

Supposing you call this module db_iterator.py, here is an example 
of use with sqlite :

    from pysqlite2 import dbapi2 as sqlite
    from db_iterator import query, Table

    conn = sqlite.connect('planes')
    query.cursor = conn.cursor()

    plane = Table()
    countries = Table()

    # all the items produced by iteration on query() are instances
    # of the Record class
    
    # simple requests
    # since no attribute of r is specified in the query, returns a list
    # of instances of Record with attributes matching all the field names
    print [ r.name for r in query(r for r in plane if r.country == 'France') ]
    
    # this request returns a list instances of Record with the attribute 
    # c_country (c.country with the . replaced by _)
    print [ country for country in query(c.country for c in countries 
            if c.continent == 'Europe') ]

    # request on two tables
    print [r.name for r in query (r for r in plane for c in countries 
            if r.country == c.country and c.continent == 'Europe')]

"""
import tokenize
import token
import types

class ge_visitor:
    """Instances of ge_visitor are used as the visitor argument to 
    compiler.walk(tree,visitor) where tree is an AST tree built by
    compiler.parse
    The instance has a src attribute which looks like the source
    code from which the tree was built
    Only a few of the visitNodeType are implemented, those likely to appear
    in a database query. Can be easily extended
    """

    def __init__(self):
        self.src = ''

    def visitTuple(self,t):
        self.src += ','.join ( [ get_source(n) for n in t.nodes ])

    def visitList(self,t):
        self.src += ','.join ( [ get_source(n) for n in t.nodes ])

    def visitMul(self,t):
        self.src += '(%s)' %('*'.join([ get_source(n) for n in t]))

    def visitName(self,t):
        self.src += t.name

    def visitConst(self,t):
        if type(t.value) is str:
            # convert single quotes, SQL-style
            self.src += "'%s'" %t.value.replace("'","''")
        else:
            self.src += str(t.value)

    def visitAssName(self,t):
        self.src += t.name

    def visitGetattr(self,t):
        self.src += '%s.%s' %(get_source(t.expr),str(t.attrname))

    def visitGenExprFor(self,t):
        self.src += 'for %s in %s ' %(get_source(t.assign),
                get_source(t.iter))
        if t.ifs:
            self.src += ' if ' +''.join([ get_source(i) for i in t.ifs ])

    def visitGenExprIf(self,t):
        self.src += get_source(t.test)

    def visitCompare(self,t):
        compiler.walk(t.expr,self)
        self.src += ' '
        for o in t.ops:
            oper = o[0]
            if oper == '==':
                oper = '='
            self.src += oper + ' '
            compiler.walk(o[1],self)

    def visitAnd(self,t):
        self.src += '('
        self.src += ' AND '.join([ get_source(n) for n in t.nodes ])
        self.src+= ')'

    def visitOr(self,t):
        self.src += '('
        self.src += ' OR '.join([ get_source(n) for n in t.nodes ])
        self.src+= ')'

    def visitNot(self,t):
        self.src += '(NOT ' + get_source(t.expr) + ')'

def get_source(node):
    """Return the source code of the node, built by an instance of
    ge_visitor"""
    return compiler.walk(node,ge_visitor()).src

class genExprVisitor:
    """Visitor used to initialize GeneratorExpression objects
    Uses the visitor pattern. See the compiler.visitor module"""

    def __init__(self):
        self.GenExprs = []

    def visitGenExprInner(self,node):
        ge = GeneratorExpression()
        self.GenExprs.append(ge)
        for y in node.getChildren():
            if y.__class__ is compiler.ast.GenExprFor:
                ge.exprfor.append(y)
            else:
                ge.result = y

class GeneratorExpression:
    """A class for a Generator Expression"""
    def __init__(self):
        self.result = None
        self.exprfor = []
        
class Record(object):
    """A generic class for database records"""
    pass

class Table:
    """A basic iterable class to avoid syntax errors"""
    def __iter__(self):
        return self
    
class query:
    """Class used for database queries
    Instance is created with query(ge) where ge is a generator
    expression
    The __init__ method builds the SQL select expression matching the
    generator expression
    Iteration on the instance of query yields the items found by
    the SQL select, under the form specified by return_type : an object,
    a dictionary or a list"""

    cursor = None   # to be set to the cursor of the connection
    return_type = object    # can be set to dict or list

    def __init__(self,s):
        self._iterating = False # used in next()

        # First we must get the source code of the generator expression
        # I use an ugly hack with stack frame attributes and tokenize
        # If there's a cleaner and safer way, please tell me !
        readline = open(s.gi_frame.f_code.co_filename).readline
        first_line = s.gi_frame.f_code.co_firstlineno
        flag = False
        self.source = ''    # the source code
        for t in tokenize.generate_tokens(open(s.gi_frame.f_code.co_filename).readline):
            # check all tokens until the last parenthesis is closed
            t_type,t_string,(r_start,c_start),(r_end,c_end),line = t
            t_name = token.tok_name[t_type]
            if r_start == first_line:
                if t_name == 'NAME' and t_string=="query":
                    flag = True
                    res = t_string
                    start = 0 # number of parenthesis
                    continue
            if flag:
                self.source += ' '+t_string
                if t_name == 'OP':
                        if t_string=='(':
                            start += 1
                        elif t_string == ')':
                            start -= 1
                            if start == 0:
                                break
        # when the source has been found, build an AST tree from it
        ast = compiler.parse(self.source.strip())
        # use a visitor to find the generator expression(s) in the source
        visitor = genExprVisitor()
        compiler.walk(ast,visitor)
        # if there are nested generator expressions, it's too difficult
        # to handle : raise an exception
        if len(visitor.GenExprs)>1:
            raise Exception('Invalid expression, found more ' \
                'than 1 generator expression')
        ge = visitor.GenExprs[0]
        self.sql = self.build_sql(ge)

    def build_sql(self,ge):
        """ Build the SQL select for the generator expression
        ge is an instance of GeneratorExpression
        The generator expression looks like
        (result) for x1 in table1 [ for x2 in table2] [ if condition ]
        It has 2 attributes :
        - result : an AST tree with the "result" part
        - exprfor : a list of AST trees, one for each "for ... in ..."
        """
        self.res = []
        if ge.result.__class__ is compiler.ast.Tuple:
            # more than one item in result
            self.res = ge.result.getChildren()
        else:
            self.res = [ge.result]
        results = [] # a list of strings = result part of the SQL expression
        for res in self.res:
            # a result can be a stand-alone name, or a "qualified" name,
            # with the table name first (table.field)
            if res.__class__ is compiler.ast.Name:
                results.append((res.name,None))
            elif res.__class__ is compiler.ast.Getattr:
                results.append((get_source(res.expr),res.attrname))
        self.results = results

        # "for x in y" produces an item in the dictionary recdefs :
        # recdef[x] = y
        recdefs = {}
        conditions = []
        for exprfor in ge.exprfor:
            recdefs[get_source(exprfor.assign)] = \
                get_source(exprfor.iter)
            if exprfor.ifs:
                # an AST tree for the condition
                conditions = exprfor.ifs

        # To build objects or dictionaries in the result set, we must
        # know the name of the fields in all the tables used in the
        # query. For this, make a simple select in each table and read
        # the information in cursor.description
        self.names={}
        for rec,table in recdefs.iteritems():
            self.cursor.execute('SELECT * FROM %s' %table)
            self.names[rec] = [ d[0] for d in self.cursor.description ]

        sql_res = [] # the way the field will appear in the SQL string
        rec_fields = [] # the name of the fields in the object or dictionary
        for (n1,n2) in results:
            if n2 is None:
                # "stand-alone" name
                if n1 in recdefs.keys():
                    sql_res += [ '%s.%s' %(n1,v) for v in self.names[n1] ]
                    rec_fields+=[ v for v in self.names[n1] ]
                else:
                    sql_res.append(n1)
                    rec_fields.append(n1)
            else:
                # "qualified" name, with the table name first
                sql_res.append('%s.%s' %(n1,n2))
                # in the result set, the object will have the attribute 
                # table_name (we can't set an attribute table.name, and
                # name alone could be ambiguous
                rec_fields.append('%s_%s' %(n1,n2))
        self.rec_fields = rec_fields
        
        # now we can build the actual SQL string
        sql = 'SELECT '+ ','.join(sql_res)
        sql += ' FROM '
        froms = []
        for (k,v) in recdefs.iteritems():
            froms.append('%s AS %s ' %(v,k))
        sql += ','.join(froms)
        if conditions:
            sql += 'WHERE '
        for c in conditions:
            sql += get_source(c)

        return sql
            
    def __iter__(self):
        return self
    
    def next(self):
        if not self._iterating:
            # begin iteration
            self.cursor.execute(self.sql)
            self._iterating = True
        row = self.cursor.fetchone()
        if row is not None:
            if self.return_type == object:
                # transform list into instance of Record
                # uses the rec_fields computed in build_sql()
                rec = Record()
                rec.__dict__ = dict(zip(self.rec_fields,row))
                return rec
            elif self.return_type == dict:
                return dict(zip(self.rec_fields,row))
            elif self.return_type == list:
                return row
        self._iterating = False
        raise StopIteration


if __name__ == "__main__":

    plane = Table()
    countries = Table()

    # all the items produced by iteration on query() are instances
    # of the Record class

    # simple requests
    # since no attribute of r is specified in the query, returns a list
    # of instances of Record with attributes matching all the field names
    q = query(r for r in plane if r.country == 'France').sql
    print(q)
    #
    # # this request returns a list instances of Record with the attribute
    # # c_country (c.country with the . replaced by _)
    # print[country
    # for country in query(c.country for c in countries
    #                      if c.continent == 'Europe') ]
    #
    # # request on two tables
    # print[r.name
    # for r in query(r for r in plane for c in countries
    #                if r.country == c.country and c.continent == 'Europe')]
