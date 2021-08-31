def unistats(df):
    import pandas as pd
    output_df = pd.DataFrame(columns=['Count','Missing','Unique','Dtype','Numeric','Mode','Mean','Min','25%','Median','75%','Max','Std','Skew', 'Kurt'])    
    for col in df:
        if pd.api.types.is_numeric_dtype(df[col]):
            output_df.loc[col] = [df[col].count(),df[col].isnull().sum(),df[col].nunique(),df[col].dtype,pd.api.types.is_numeric_dtype(df[col]),df[col].mode().values[0],
   df[col].mean(),df[col].min(),df[col].quantile(0.25),df[col].median(),df[col].quantile(0.75),df[col].max(),df[col].std(),df[col].skew(),df[col].kurt()]
        else:
            output_df.loc[col] = [df[col].count(),df[col].isnull().sum(),df[col].nunique(),df[col].dtype,pd.api.types.is_numeric_dtype(df[col]),df[col].mode().values[0],'-','-','-','-','-','-','-','-','-']
    return output_df.sort_values(by=['Numeric','Skew','Unique'], ascending= False)

def anova(df, feature, label):
    import pandas as pd
    import numpy as np
    from scipy import stats
    
    groups = df[feature].unique()
    df_grouped = df.groupby(feature)
    grouped_labels = []
    for g in groups:
        g_list = df_grouped.get_group(g) #i think this equal df[df.feature == group #a,b,c,d,e]
        grouped_labels.append(g_list[label])
    
    return stats.f_oneway(*grouped_labels)


def heteroscedasticity(df, feature,label):
    from statsmodels.stats.diagnostic import het_breuschpagan
    from statsmodels.stats.diagnostic import het_white #two version of a heu test # để thấy spread ở các vùng khác nhau của data
    #sự chính xác phụ thuộc vào input của ta, input nằm ở vùng het thấp thì chính xác hơn 
    import pandas as pd
    import statsmodels.api as sm
    from statsmodels.formula.api import ols


    model = ols(formula = (label + '~' + feature), data =df).fit() #formula order y first then x

    output_df = pd.DataFrame(columns=['LM stat', 'LM p-value', 'F-stat', 'F p-value'])

    try:
        white_test = het_white(model.resid(), model.model.exog )#residual, #grab the independent var
        output_df.loc['White'] = white_test
    except:
        print('Unable to run white test of heteroscedasticity')

    breuschpagan_test = het_breuschpagan(model.resid, model.model.exog)
    
    output_df.loc['Br-Pa'] = breuschpagan_test

    return output_df.round(3)

def scatter(feature,label):
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
    from scipy import stats
    
    #calculate the regression line
    m, b, r, p, err = stats.linregress(feature,label)
    
    textstr = 'y =' +str(round(m,2)) + 'x+ ' + str(round(b,2)) + '\n' 
    textstr += 'r2 =' + str(round(r**2,2)) + '\n'
    textstr += 'p =' + str(round(p,2)) + '\n'
    textstr += str(feature.name) + 'skew =' +str(round(feature.skew(),2)) +'\n'
    textstr += str(label.name) + 'skew =' +str(round(feature.skew(),2))
    textstr += str(heteroscedasticity(pd.DataFrame(label).join(pd.DataFrame(feature)),feature.name,label.name))
    sns.set(color_codes =True)
    ax = sns.jointplot(x=feature,y=label, kind='reg')
    ax.fig.text(1, 0.114, textstr, fontsize =12, transform=plt.gcf().transFigure)
    plt.show()



def bar_chart(df,feature,label):
    import pandas as pd
    from scipy import stats
    import matplotlib.pyplot as plt
    import seaborn as sns

    groups = df[feature].unique()
    df_grouped = df.groupby(feature)
    group_labels =[]
    for g in groups:
        g_list = df_grouped.get_group(g)
        group_labels.append(g_list[label])

    #Now calculate the ANOVA results
    oneway = stats.f_oneway(*group_labels)

    #Next, calculate t-tests with Bonferroni correction for p-value threshold
    unique_groups = df[feature].unique()
    ttests =[]
    for i,group in enumerate(unique_groups):
        for i2, group_2 in enumerate(unique_groups):
            if i2>i:
                type_1 = df[df[feature] == group]
                type_2 = df[df[feature] == group]

                #there must be more than 1 case per group to perform a t-test
                if len(type_1[label]) < 2 or len(type_2[label]) < 2:
                    print("'" + group + "' n =" + str(len(type_1)) + "; '" + group_2 + "' n =" + str(len(type_2)) +"; no t-test performed")
                else:
                    t,p = stats.ttest_ind(type_1[label], type2[label])
                    ttests.append([group, group_2, t.round(4), p.round(4)])

    if len(ttests) > 0:		#Avoid 'Divided by 0' error
        p_threshold = 0.05/ len(ttests) #Bonferroni-corrected p-value determined
    else:
        p_threshold = 0.05

    #Add all descriptive statistics to the diagram
    textstr = '	ANOVA' + '\n'
    textstr += 'F:		'+str(oneway[0].round(2)) +'\n'
    textstr += 'p-value:	'+str(oneway[1].round(2)) +'\n\n'
    textstr += 'Sig. Comparisons (Bonferroni-corrected)' +'\n'
    for ttest in ttests:
        if ttest[3] <= p_threshold:
            textstr += ttest[0] + '-' + ttest[1] + ": t=" + str(ttest[2]) + ", p=" + str(ttest[3]) + '\n'

    ax = sns.barplot(df[feature], df[label])
    ax.text(1,0.1, textstr, fontsize = 12, transform =plt.gcf().transFigure)
    plt.show()

def bivstats(df,label):
    from scipy import stats
    import pandas as pd
    import numpy as np
    #create an empty DataFrame to store output
    output_df = pd.DataFrame(columns = ['Stat', '+/-','Effect size','p-value'])
    for col in df:
        if not col == label:
            if df[col].isnull().sum() ==0:
                if pd.api.types.is_numeric_dtype(df[col]):  #Only calculate r,p-value for the numeric columns
                    r,p = stats.pearsonr(df[label], df[col])
                    output_df.loc[col] = ['r',np.sign(r),abs(round(r,3)), round(p,6)]
                    scatter(df[col], df[label]) 
                else:                 #rather than passing whole df, just pass the df[[col,label]] for faster
                    F, p = anova(df[[col,label]],col,label)
                    output_df.loc[col] = ['F','',round(F,3),round(p,6)]
                    bar_chart(df,col,label)
            else:
                output_fd.loc[col] = [np.nan, np.nan, np.nan, np.nan]


    return output_df.sort_values(by=['Stat','Effect size'],ascending=[False,False])


def bivstats_table(df,label):
    from scipy import stats
    import pandas as pd
    import numpy as np
    #create an empty DataFrame to store output
    output_df = pd.DataFrame(columns = ['Stat', '+/-','Effect size','p-value'])
    for col in df:
        if not col == label:
            if df[col].isnull().sum() ==0:
                if pd.api.types.is_numeric_dtype(df[col]):  #Only calculate r,p-value for the numeric columns
                    r,p = stats.pearsonr(df[label], df[col])
                    output_df.loc[col] = ['r',np.sign(r),abs(round(r,3)), round(p,6)]
                else:                 #rather than passing whole df, just pass the df[[col,label]] for faster
                    F, p = anova(df[[col,label]],col,label)
                    output_df.loc[col] = ['F','',round(F,3),round(p,6)]
            else:
                output_fd.loc[col] = [np.nan, np.nan, np.nan, np.nan]


    return output_df.sort_values(by=['Stat','Effect size'],ascending=[False,False])