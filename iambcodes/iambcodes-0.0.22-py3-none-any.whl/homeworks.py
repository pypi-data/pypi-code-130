import random as rd
import numpy as np

def initiate_homework(matricnb, counter):   
    try:
        if type(matricnb) == int and type(counter) == int:
            print("Matriculation-Number accepted.\n\nGenerating random numbers..")
            print("Matriculation-Number accepted.\n\nGenerating personalized homework parameters..")

            #RNG for this homework
            rd.seed(matricnb)
            
            listofrndms = [rd.random() for i in range(counter)] #create new random numbers that can be used to modify parameters
        elif matricnb == "test":
            print("Testing functionality!")
            return "test"
        else:
            print("ATTENTION! Your input was not in the right format.\nPlease make sure the variable looks like this:\n\nExample: matricnb = 2022\n\nand try again")

    except:
        print("An ERROR has occured. This should not have happened.\n\n")
    return(listofrndms)

def initiate_question_three_one(listofrndms):
    #Parameters for this homework
    if type(listofrndms) == list:
        newYxs = 1+round(listofrndms[0],1) #range 1.0-2.0
        newH = 1.5+round((listofrndms[1]*0.5),1) #range 1.5-2.0
        newO = 0.3+round((listofrndms[2]*0.4),1) #range 0.3-0.7
        newN = 0.1+round((listofrndms[3]*0.2),1) #range 0.1-0.3


        #Print the parameters
        print("##########\n\nParameters for Question 1:")
        print("Your glucose yield Y_(XS) is {} C-mol glucose/C-mol biomass".format(newYxs))
        print("Your biomass composition is CH_({})O_({})N_({})\n\n##########".format(newH,newO,round(newN,1)))#Comment: the round is nessary because of a bug...

    elif matricnb == "test":
        newYxs = 2
        newH = 1.8
        newO = 0.5
        newN = 0.2
        print("Testing functionality!")

    else:
        print("ATTENTION! Your input was not in the right format.\nPlease make sure the function call was not changed")
      
    return (newYxs, newH, newO, newN, 0)#toggles help_question_1_toggle to 0, helpoption was not used

def initiate_question_three_two(listofrndms):
    if type(listofrndms) == list:
            newRO2 = 3000+round((listofrndms[4]*500)) #range 3000-3500)
            newRCO2 = 8000+round((listofrndms[5]*500)) #range 8000-8500)
            
            print("##########\n\n\nParameters for Question 2:")
            print("Your O_2 Exchange-Rate is {} mol/h".format(newRO2))
            print("Your CO_2 Exchange-Rate is {} mol/h\n\n##########".format(newRCO2))
    elif matricnb == "test":
        newRO2 = 3300
        newRCO2 = 8300
        print("Testing functionality!")

    else:
        print("ATTENTION! Your input was not in the right format.\nPlease make sure the function call was not changed")
      
    return (newRO2, newRCO2, 0)#toggles help_question_2_toggle to 0, helpoption was not used
            
#
# Homework Question Tipps
# Scripts to print out Tipps for Question 1 and 2

def load_homework_three_question_one_tipp():
    
    helptext = "##########\n" \
    "The RQ is rate of CO_2 production, divivided by the rate of O_2 production\n" \
    "RQ = r(CO_2)/r(O_2)\n" \
    "Yields correlate directly to rates\n" \
    "RQ = r(CO_2)/r(O_2) = Y(CO_2)/Y(O_2)\n\n" \
    "By calculating all yields for the known reaction, you will be able to identify the required yields\n" \
    "##########"
    
    
    return(helptext, 1)##toggles help_question_1_toggle to 1, helpoption was used

def load_homework_three_question_two_tipp():
    
    helptext = "##########\n" \
    "Don't forget, that for Question 2, Ethanol is an additional product!\nYou also need to subtract the ash from the assumed Biomass.\n\n"\
    "First, convert the biomass concentration from g/L to c-mol\n" \
    "and normalize the gas exchange rates for  O_2 and CO_2\n" \
    "You already have the growth rate. You can use it to and the exchange rates to determine the\nyields of O_2 and CO_2\n" \
    "With that, the rest of the stoichiometric matrix for the equation is solvable\n"
    "##########\n"
    
    return(helptext, 1)#toggles help_question_2_toggle to 1, helpoption was used
    #return(1, helptext)
#
# Homework Solution Check
# Scripts to check student solution and print out a hashcode to upload in the Moodle-course for Question 1 and 2

def correct_homework_three_question_one(RQ, newYxs, newH, newO, newN, hq1tgl):
    try:
        rndint = rd.randrange(9)
        
        Yxc = newYxs - 1
        #print(Yxc)
        Yxn = newN
        Yxw = (newYxs*2 + Yxn*3 - newH)/2
        #print(Yxw)
        Yxo = (-newYxs + Yxw + 2*Yxc + newO)/2
        #print(Yxo)

        realRQ = Yxc/Yxo
        #print(realRQ)

        #Check if student solution is correct
        #Assumes aswer was rounded to 2 decimals
        if round(realRQ,2) == RQ:
            print("Solution corect! RQ is {}".format(realRQ))
            if hq1tgl == 0:
                print("Here's your code!\n\n{}\n\nPlease upload it in the designated Moodle-Task.".format((((rndint+50)**2*10)+hq1tgl)*10+rndint))                                                                                                  
                                                                                                          
            elif hq1tgl == 1:
                print("Here's your code!\n\n{}\n\nPlease upload it in the designated Moodle-Task.".format((((rndint+50)**2*10)+hq1tgl)*10+rndint))                                                                                                  
            else:
                print("Solution right but something in the function went wrong.\nAnyway... ")
                print("Here's your code!\n\n{}\n\nPlease upload it in the designated Moodle-Task.".format((((rndint+50)**2*10)+2)*10+rndint))
        else:
            print("Solution WRONG!\nDon't give up and try again!")
    except:
        print("This message should not occur, did you change anything? lease check if your Solution is in the right format!")

#
#
#

def correct_homework_three_question_two(Yield_Substrate, Yield_Ethanol, newYxs, newH, newO, newN, newRO2, newRCO2, hq2tgl):
    try:
        rndint = rd.randrange(9)

        #1. Converting biomass concentration from g/l to c-mol
        Xn = (round(46.5/(1*12+newH*1+newO*16+newN*14),2)*10000) #Xn = ((50 g/L - 7 % ash)/(masses of C_1+H_newH+O_newO+N_newN) g/mol) * 10000 L = x cmol

        #2. Normalizing gas exchange rates
        rO2 = round(newRO2/Xn,2)
        rCO2 = round(newRCO2/Xn,2)

        #3. Calculating Yields, YXO, YXC
        mu = 0.35 #Growthrate = 0.35 1/h
        Yxo = rO2/mu
        Yxc = rCO2/mu
        Yxn = newN

        Ymatrixvar = np.array([[2,1],[1,-0.5]])
        Ymatrixsolvd = np.array([-1*(newH-2-2*Yxc-3*Yxn), -1*(newO+1*Yxc-1-2*Yxo)])
        Ymatrix = np.linalg.solve(Ymatrixvar,Ymatrixsolvd)
        Yxw,Yxe = Ymatrix
        Yxs = Yxe+1+Yxc

        #Check if student solution is correct
        #Assumes aswer was rounded to 2 decimals
        if round(Yxs,2) == Yield_Substrate and round(Yxe,2) == Yield_Ethanol:
            print("Solution corect! Substrate yield is {}\nand Ethanol yield is {}".format(Yxs,Yxe))
            
            if hq2tgl == 0:
                print("Here's your code!\n\n{}\n\nPlease upload it in the designated Moodle-Task.".format((((rndint+10)**3*10)+hq2tgl)*10+rndint))                                                                                                  
                                                                                                          
            elif hq2tgl == 1:
                print("Here's your code!\n\n{}\n\nPlease upload it in the designated Moodle-Task.".format((((rndint+10)**3*10)+hq2tgl)*10+rndint))                                                                                                  
            else:
                print("Solution right but something in the function went wrong.\nAnyway... ")
                print("Here's your code!\n\n{}\n\nPlease upload it in the designated Moodle-Task.".format((((rndint+10)**3*10)+2)*10+rndint))
        elif round(Yxs,2) == Yield_Substrate and round(Yxe,2) != Yield_Ethanol:
            print("Ethanol yield WRONG!\nPlease try again!")
        elif round(Yxs,2) != Yield_Substrate and round(Yxe,2) == Yield_Ethanol:
            print("Substrate yield WRONG!\nPlease try again!")
        else:
            print("Real Yxe={}\nStudent_Ethanol_Yield={}".format(Yxe,Yield_Ethanol))
            print("Real Yxs={}\nStudent_Substrate_Yield={}".format(Yxs,Yield_Substrate))
            print("Solution WRONG!\nDon't give up and try again!")
    except:
        print("This message should not occur, did you change anything? lease check if your Solution is in the right format!")