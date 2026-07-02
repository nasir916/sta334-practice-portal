import re

def normalize_r_code(code):
    """
    Standardizes R code:
    - Strips spaces, standardizes assignment <- to =
    - Replaces double quotes with single quotes
    - Standardizes pipes |> to %>%
    - Replaces smart quotes
    """
    if not code:
        return ""
    
    # Lowercase for function calls but keep variable names?
    # R is case-sensitive, so we should keep casing, but strip whitespaces
    c = code.strip()
    
    # Replace smart quotes
    c = c.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    
    # Replace double quotes with single quotes
    c = re.sub(r'"', "'", c)
    
    # Normalize pipe operators: standard R |> to %>%
    c = c.replace("|>", "%>%")
    
    # Normalize assignment operator: <- to =
    c = c.replace("<-", "=")
    
    # Remove all spaces around operators (=, +, -, *, /, %, >, <, ,, (, ), %>% )
    operators = [r'\=', r'\+', r'\-', r'\*', r'\/', r'\%', r'\>', r'\<', r'\,', r'\(', r'\)', r'\%>\%']
    for op in operators:
        c = re.sub(r'\s*' + op + r'\s*', op.replace('\\', ''), c)
        
    # Strip multiple whitespaces
    c = re.sub(r'\s+', ' ', c)
    return c.strip()

def grade_question(set_idx, q_no, sub_no, student_ans):
    """
    Grades a subquestion.
    Returns: (score, max_marks, feedback_str)
    """
    student_ans = student_ans.strip() if student_ans else ""
    
    if not student_ans:
        return 0, get_max_marks(set_idx, q_no, sub_no), "No answer provided."
        
    normalized_student = normalize_r_code(student_ans)
    
    # Define rules per question
    key = (set_idx, q_no, sub_no)
    
    # Fallback to direct matches if not defined in rules
    max_marks = get_max_marks(set_idx, q_no, sub_no)
    
    # GRADING LOGIC
    # ==================== PRACTICE SET 1 ====================
    if set_idx == 1:
        if q_no == 1:
            if sub_no == 'a': # market_data <- read.csv("market_survey.csv") [2 marks]
                # Check for market_data = read.csv('market_survey.csv')
                # Also accept without market_data prefix for partial
                if "market_data=read.csv('market_survey.csv')" in normalized_student:
                    return 2.0, 2, "Correct read.csv syntax and assignment."
                elif "read.csv('market_survey.csv')" in normalized_student:
                    return 1.0, 2, "Correct read.csv call, but missing or incorrect assignment to variable 'market_data'."
                elif "market_data" in student_ans and "read.csv" in student_ans:
                    return 1.0, 2, "Contains correct function and variable, but syntax is incorrect."
                return 0.0, 2, "Incorrect. Expected: market_data <- read.csv('market_survey.csv')"
                
            elif sub_no == 'b': # library(readxl) read_excel("stall_list.xlsx", sheet = 2) [1 mark]
                score = 0.0
                feedback = []
                if "library('readxl')" in normalized_student or "library(readxl)" in normalized_student or "require(readxl)" in normalized_student:
                    score += 0.5
                    feedback.append("Loaded library(readxl).")
                if "read_excel('stall_list.xlsx',sheet=2)" in normalized_student or "read_excel('stall_list.xlsx',2)" in normalized_student:
                    score += 0.5
                    feedback.append("Correct read_excel syntax with sheet=2.")
                elif "read_excel" in student_ans:
                    feedback.append("Contains read_excel but arguments are incorrect.")
                
                if score == 0.0:
                    return 0.0, 1, "Incorrect. Expected: library(readxl); read_excel('stall_list.xlsx', sheet = 2)"
                return score, 1, " | ".join(feedback)
                
            elif sub_no == 'c': # write.csv(clean_data, "market_clean.csv", row.names = FALSE) [2 marks]
                score = 0.0
                feedback = []
                if "write.csv(clean_data,'market_clean.csv'" in normalized_student:
                    score += 1.0
                    feedback.append("Correct write.csv function and arguments.")
                if "row.names=FALSE" in normalized_student or "row.names=F" in normalized_student:
                    score += 1.0
                    feedback.append("Correct row.names=FALSE argument.")
                
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: write.csv(clean_data, 'market_clean.csv', row.names = FALSE)"
                return score, 2, " | ".join(feedback)
                
        elif q_no == 2:
            if sub_no == 'a': # ggplot bar chart [4 marks]
                score = 0.0
                feedback = []
                if "library(ggplot2)" in normalized_student or "library('ggplot2')" in normalized_student:
                    score += 1.0
                    feedback.append("Loaded ggplot2 library.")
                else:
                    # check if they have ggplot2 load
                    feedback.append("Missing library(ggplot2).")
                
                if "ggplot(pasar_data,aes(x=Stall_Category))" in normalized_student:
                    score += 1.0
                    feedback.append("Correct ggplot base with dataset and aesthetics.")
                elif "ggplot(pasar_data" in normalized_student:
                    score += 0.5
                    feedback.append("ggplot base has dataset but incorrect aesthetics.")
                    
                if "geom_bar(fill='orange')" in normalized_student:
                    score += 1.0
                    feedback.append("Correct geom_bar with fill='orange'.")
                elif "geom_bar(" in normalized_student:
                    score += 0.5
                    feedback.append("Added geom_bar layer, but missing fill='orange'.")
                    
                if "labs(" in normalized_student and ("title=" in normalized_student or "x=" in normalized_student or "y=" in normalized_student):
                    score += 1.0
                    feedback.append("Added titles and labels.")
                
                if score == 0.0:
                    return 0.0, 4, "Incorrect. Check ggplot syntax, geom_bar(fill='orange'), and labs()."
                return score, 4, " | ".join(feedback)
                
            elif sub_no == 'b': # ggplot boxplot [3 marks]
                score = 0.0
                feedback = []
                if "ggplot(pasar_data,aes(x=Day_Type,y=Daily_Sales))" in normalized_student or "ggplot(pasar_data,aes(y=Daily_Sales,x=Day_Type))" in normalized_student:
                    score += 2.0
                    feedback.append("Correct ggplot base with Day_Type and Daily_Sales aesthetics.")
                elif "ggplot(pasar_data" in normalized_student:
                    score += 1.0
                    feedback.append("ggplot base has dataset but incorrect aesthetics mapping.")
                    
                if "geom_boxplot()" in normalized_student:
                    score += 1.0
                    feedback.append("Correct geom_boxplot() layer.")
                
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: ggplot(pasar_data, aes(x = Day_Type, y = Daily_Sales)) + geom_boxplot()"
                return score, 3, " | ".join(feedback)
                
            elif sub_no == 'c': # Boxplot interpretation [3 marks]
                score = 0.0
                feedback = []
                ans_lower = student_ans.lower()
                # Check Weekday median (approx RM500)
                if "weekday" in ans_lower and ("500" in ans_lower or "500" in ans_lower):
                    score += 1.0
                    feedback.append("Correct Weekday median.")
                # Check Weekend median (approx RM900)
                if "weekend" in ans_lower and ("900" in ans_lower or "900" in ans_lower):
                    score += 1.0
                    feedback.append("Correct Weekend median.")
                # Check larger spread
                if "larger spread" in ans_lower or "spread" in ans_lower:
                    if "weekend" in ans_lower:
                        score += 1.0
                        feedback.append("Correctly identified Weekend has larger spread.")
                elif "weekend" in ans_lower and score < 2.0: # fallback
                    score += 1.0
                    feedback.append("Weekend identified (larger spread).")
                
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: Weekday median ~500, Weekend ~900, Weekend has larger spread."
                return score, 3, " | ".join(feedback)
                
        elif q_no == 3:
            if sub_no == 'a': # dplyr top_stalls [3 marks]
                score = 0.0
                feedback = []
                # Check pipe and assignment
                if "top_stalls=stall_data" in normalized_student or "top_stalls<-stall_data" in normalized_student:
                    # assignment correct
                    pass
                
                if "select(Stall,Daily_Sales)" in normalized_student or "select(Daily_Sales,Stall)" in normalized_student:
                    score += 1.0
                    feedback.append("Correct select columns.")
                if "filter(Daily_Sales>700)" in normalized_student:
                    score += 1.0
                    feedback.append("Correct filter condition (> 700).")
                if "top_stalls=" in normalized_student or "top_stalls<-" in student_ans:
                    score += 1.0
                    feedback.append("Correctly saved output to top_stalls.")
                
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: top_stalls <- stall_data %>% select(Stall, Daily_Sales) %>% filter(Daily_Sales > 700)"
                return score, 3, " | ".join(feedback)
                
            elif sub_no == 'b': # arrange sales_rank [2 marks]
                score = 0.0
                feedback = []
                if "sales_rank=stall_data" in normalized_student:
                    score += 0.5
                    feedback.append("Assigned to sales_rank.")
                if "arrange(desc(Daily_Sales))" in normalized_student:
                    score += 1.5
                    feedback.append("Correct arrange descending.")
                elif "arrange(-Daily_Sales)" in normalized_student:
                    score += 1.5
                    feedback.append("Correct arrange descending using negative syntax.")
                elif "arrange(Daily_Sales)" in normalized_student:
                    score += 0.5
                    feedback.append("Arranged ascending instead of descending.")
                
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: sales_rank <- stall_data %>% arrange(desc(Daily_Sales))"
                return score, 2, " | ".join(feedback)
                
            elif sub_no == 'c': # mutate Profit [2 marks]
                score = 0.0
                feedback = []
                if "mutate(Profit=Daily_Sales-Cost)" in normalized_student or "mutate(Profit=Daily_Sales-Cost)" in normalized_student:
                    score += 2.0
                    feedback.append("Correct mutate expression.")
                elif "mutate(" in normalized_student and "Profit" in normalized_student:
                    score += 1.0
                    feedback.append("Mutate function used but syntax contains errors.")
                
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: stall_data <- stall_data %>% mutate(Profit = Daily_Sales - Cost)"
                return score, 2, " | ".join(feedback)
                
            elif sub_no == 'd': # group_by summarise Avg_Profit [3 marks]
                score = 0.0
                feedback = []
                if "group_by(Category)" in normalized_student:
                    score += 1.5
                    feedback.append("Correct group_by(Category).")
                if "summarise(Avg_Profit=mean(Profit))" in normalized_student or "summarize(Avg_Profit=mean(Profit))" in normalized_student:
                    score += 1.5
                    feedback.append("Correct summarise(Avg_Profit = mean(Profit)).")
                elif "summarise" in normalized_student or "summarize" in normalized_student:
                    score += 0.5
                    feedback.append("Used summarise but calculation is incorrect.")
                
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: category_summary <- stall_data %>% group_by(Category) %>% summarise(Avg_Profit = mean(Profit))"
                return score, 3, " | ".join(feedback)

    # ==================== PRACTICE SET 2 ====================
    elif set_idx == 2:
        if q_no == 1:
            if sub_no == 'a': # library(haven); commuter_data <- read_sav("commuter.sav") [2 marks]
                score = 0.0
                feedback = []
                if "library(haven)" in normalized_student or "library('haven')" in normalized_student:
                    score += 1.0
                    feedback.append("Loaded library(haven).")
                if "commuter_data=read_sav('commuter.sav')" in normalized_student:
                    score += 1.0
                    feedback.append("Correct read_sav syntax and assignment.")
                elif "read_sav('commuter.sav')" in normalized_student:
                    score += 0.5
                    feedback.append("Correct read_sav call but missing assignment.")
                
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: library(haven); commuter_data <- read_sav('commuter.sav')"
                return score, 2, " | ".join(feedback)
                
            elif sub_no == 'b': # library(readr); read_csv("https://data.gov.my/transport.csv") [1 mark]
                score = 0.0
                feedback = []
                if "library(readr)" in normalized_student or "library('readr')" in normalized_student:
                    score += 0.5
                    feedback.append("Loaded library(readr).")
                if "read_csv('https://data.gov.my/transport.csv')" in normalized_student:
                    score += 0.5
                    feedback.append("Correct read_csv URL import.")
                
                if score == 0.0:
                    return 0.0, 1, "Incorrect. Expected: library(readr); read_csv('https://data.gov.my/transport.csv')"
                return score, 1, " | ".join(feedback)
                
            elif sub_no == 'c': # State TWO other file formats [2 marks]
                score = 0.0
                feedback = []
                ans_lower = student_ans.lower()
                formats = [
                    ('excel', ['excel', '.xlsx', '.xls']),
                    ('stata', ['stata', '.dta']),
                    ('sas', ['sas', '.sas7bdat']),
                    ('text', ['text', 'txt', 'tab-delimited', 'tsv']),
                    ('json', ['json']),
                    ('xml', ['xml']),
                ]
                matched = 0
                for fmt_name, keywords in formats:
                    if any(kw in ans_lower for kw in keywords):
                        matched += 1
                        feedback.append(fmt_name.capitalize())
                        score += 1.0
                        if matched == 2:
                            break
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected formats: Excel (.xlsx), Stata (.dta), text (.txt), JSON, SAS."
                return score, 2, f"Correct formats identified: {', '.join(feedback)}"
                
        elif q_no == 2:
            if sub_no == 'a': # line chart [4 marks]
                score = 0.0
                feedback = []
                if "library(ggplot2)" in normalized_student:
                    score += 1.0
                    feedback.append("Loaded ggplot2.")
                if "ggplot(monthly_riders,aes(x=Month,y=Passengers))" in normalized_student or "ggplot(monthly_riders,aes(y=Passengers,x=Month))" in normalized_student:
                    score += 1.0
                    feedback.append("Correct base mapping (Month & Passengers).")
                if "geom_line(color='green')" in normalized_student or "geom_line(colour='green')" in normalized_student:
                    score += 1.0
                    feedback.append("Correct geom_line layer with green color.")
                elif "geom_line(" in normalized_student:
                    score += 0.5
                    feedback.append("Added geom_line but missing green color.")
                if "labs(" in normalized_student:
                    score += 1.0
                    feedback.append("Added labels and titles.")
                    
                if score == 0.0:
                    return 0.0, 4, "Incorrect. Expected: ggplot(monthly_riders, aes(x = Month, y = Passengers)) + geom_line(color = 'green') + labs(...)"
                return score, 4, " | ".join(feedback)
                
            elif sub_no == 'b': # stacked bar route Ticket_Type [3 marks]
                score = 0.0
                feedback = []
                if "ggplot(trip_data,aes(x=Route,fill=Ticket_Type))" in normalized_student:
                    score += 2.0
                    feedback.append("Correct mapping: x=Route, fill=Ticket_Type.")
                elif "ggplot(trip_data" in normalized_student:
                    score += 1.0
                    feedback.append("ggplot base dataset is correct.")
                
                if "geom_bar(" in normalized_student:
                    score += 1.0
                    feedback.append("Correct geom_bar layer.")
                    
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: ggplot(trip_data, aes(x = Route, fill = Ticket_Type)) + geom_bar()"
                return score, 3, " | ".join(feedback)
                
            elif sub_no == 'c': # stack vs dodge [3 marks]
                score = 0.0
                feedback = []
                ans_lower = student_ans.lower()
                if "stack" in ans_lower and ("top" in ans_lower or "accumulate" in ans_lower or "segment" in ans_lower or "vertical" in ans_lower):
                    score += 1.0
                    feedback.append("Explained stack (stacked segments).")
                if "dodge" in ans_lower and ("side" in ans_lower or "next to" in ans_lower or "parallel" in ans_lower):
                    score += 1.0
                    feedback.append("Explained dodge (side-by-side).")
                if "dodge" in ans_lower and ("suitable" in ans_lower or "compare" in ans_lower or "more" in ans_lower):
                    score += 1.0
                    feedback.append("Identified dodge as more suitable for side-by-side comparison.")
                elif "dodge" in ans_lower and score < 2.0:
                    score += 1.0
                    feedback.append("Identified dodge as better.")
                    
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Explain that 'stack' piles segments vertically and 'dodge' places them side by side, making 'dodge' better."
                return score, 3, " | ".join(feedback)
                
        elif q_no == 3:
            if sub_no == 'a': # output of mean without na.rm [1 mark]
                if "na" in student_ans.upper():
                    return 1.0, 1, "Correct. Output will be NA because of missing values."
                return 0.0, 1, "Incorrect. Expected: NA."
                
            elif sub_no == 'b': # mean with na.rm = TRUE [3 marks]
                if "mean(bus_data$Passengers,na.rm=TRUE)" in normalized_student or "mean(bus_data$Passengers,na.rm=T)" in normalized_student:
                    return 3.0, 3, "Correct mean command with na.rm=TRUE."
                elif "mean" in normalized_student and "na.rm=TRUE" in normalized_student:
                    return 2.0, 3, "Correct function and na.rm parameter, but variable path is incorrect."
                elif "na.rm=TRUE" in normalized_student or "na.rm=T" in normalized_student:
                    return 1.5, 3, "Identified na.rm = TRUE argument."
                return 0.0, 3, "Incorrect. Expected: mean(bus_data$Passengers, na.rm = TRUE)"
                
            elif sub_no == 'c': # rename Complaints [2 marks]
                score = 0.0
                feedback = []
                if "bus_renamed=bus_data" in normalized_student:
                    score += 0.5
                    feedback.append("Assigned to bus_renamed.")
                if "rename(Feedback_Count=Complaints)" in normalized_student:
                    score += 1.5
                    feedback.append("Correct rename syntax (NewName = OldName).")
                elif "rename(Complaints=Feedback_Count)" in normalized_student:
                    score += 0.5
                    feedback.append("Incorrect rename argument order (OldName = NewName instead of NewName = OldName).")
                
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: bus_renamed <- bus_data %>% rename(Feedback_Count = Complaints)"
                return score, 2, " | ".join(feedback)
                
            elif sub_no == 'd': # select and filter [2 marks]
                score = 0.0
                feedback = []
                if "select(Route,Passengers)" in normalized_student or "select(Passengers,Route)" in normalized_student:
                    score += 1.0
                    feedback.append("Correct columns selected.")
                if "filter(Passengers>400)" in normalized_student:
                    score += 1.0
                    feedback.append("Correct filter condition.")
                
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: busy_routes <- bus_data %>% select(Route, Passengers) %>% filter(Passengers > 400)"
                return score, 2, " | ".join(feedback)
                
            elif sub_no == 'e': # arrange descending passengers [2 marks]
                score = 0.0
                feedback = []
                if "route_rank=bus_data" in normalized_student:
                    score += 0.5
                    feedback.append("Assigned to route_rank.")
                if "arrange(desc(Passengers))" in normalized_student or "arrange(-Passengers)" in normalized_student:
                    score += 1.5
                    feedback.append("Correct descending sort.")
                elif "arrange(Passengers)" in normalized_student:
                    score += 0.5
                    feedback.append("Sorted ascending instead of descending.")
                
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: route_rank <- bus_data %>% arrange(desc(Passengers))"
                return score, 2, " | ".join(feedback)

    # ==================== PRACTICE SET 3 ====================
    elif set_idx == 3:
        if q_no == 1:
            if sub_no == 'a': # oven_data <- read.table("oven_log.txt", header = TRUE, sep = ";") [2 marks]
                score = 0.0
                feedback = []
                if "oven_data=read.table('oven_log.txt'" in normalized_student:
                    score += 0.5
                    feedback.append("Correct read.table function call.")
                if "header=TRUE" in normalized_student or "header=T" in normalized_student:
                    score += 0.5
                    feedback.append("Correct header=TRUE.")
                if "sep=';'" in normalized_student:
                    score += 1.0
                    feedback.append("Correct separator ';'.")
                    
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: oven_data <- read.table('oven_log.txt', header = TRUE, sep = ';')"
                return score, 2, " | ".join(feedback)
                
            elif sub_no == 'b': # purpose of header=TRUE [1 mark]
                ans_lower = student_ans.lower()
                if "first row" in ans_lower or "variable name" in ans_lower or "column name" in ans_lower or "header" in ans_lower or "title" in ans_lower:
                    return 1.0, 1, "Correct. header = TRUE specifies the first row contains variable names."
                return 0.0, 1, "Incorrect. Explain that it tells R the first row contains column names, not data."
                
            elif sub_no == 'c': # write.csv row.names=FALSE [2 marks]
                score = 0.0
                feedback = []
                if "write.csv(daily_report,'report_today.csv'" in normalized_student:
                    score += 1.0
                    feedback.append("Correct write.csv arguments.")
                if "row.names=FALSE" in normalized_student or "row.names=F" in normalized_student:
                    score += 1.0
                    feedback.append("Correct row.names=FALSE parameter.")
                
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: write.csv(daily_report, 'report_today.csv', row.names = FALSE)"
                return score, 2, " | ".join(feedback)
                
        elif q_no == 2:
            if sub_no == 'a': # histogram binwidth=5 fill=brown [4 marks]
                score = 0.0
                feedback = []
                if "library(ggplot2)" in normalized_student:
                    score += 1.0
                    feedback.append("Loaded library(ggplot2).")
                if "ggplot(sales_daily,aes(x=Items_Sold))" in normalized_student:
                    score += 1.0
                    feedback.append("Correct ggplot base mapping x=Items_Sold.")
                if "geom_histogram(" in normalized_student:
                    # check parameters
                    if "binwidth=5" in normalized_student:
                        score += 1.0
                        feedback.append("Correct binwidth=5.")
                    else:
                        feedback.append("Missing binwidth=5 parameter.")
                    if "fill='brown'" in normalized_student:
                        score += 1.0
                        feedback.append("Correct fill='brown'.")
                    else:
                        feedback.append("Missing fill='brown' parameter.")
                
                if score == 0.0:
                    return 0.0, 4, "Incorrect. Expected: ggplot(sales_daily, aes(x = Items_Sold)) + geom_histogram(binwidth = 5, fill = 'brown') + labs(...)"
                return score, 4, " | ".join(feedback)
                
            elif sub_no == 'b': # clustered bar chart shift side-by-side [3 marks]
                score = 0.0
                feedback = []
                if "ggplot(sales_daily,aes(x=Branch,fill=Shift))" in normalized_student:
                    score += 2.0
                    feedback.append("Correct mapping: x=Branch, fill=Shift.")
                if "geom_bar(position='dodge')" in normalized_student:
                    score += 1.0
                    feedback.append("Correct position='dodge' for clustered bars.")
                elif "geom_bar(" in normalized_student:
                    feedback.append("Added geom_bar layer but missing position='dodge' parameter.")
                    
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: ggplot(sales_daily, aes(x = Branch, fill = Shift)) + geom_bar(position = 'dodge')"
                return score, 3, " | ".join(feedback)
                
            elif sub_no == 'c': # histogram interpretation [3 marks]
                score = 0.0
                feedback = []
                ans_lower = student_ans.lower()
                if "skewed to the left" in ans_lower or "left" in ans_lower or "negatively skewed" in ans_lower:
                    score += 1.0
                    feedback.append("Correctly identified skewed-left shape.")
                if "40" in ans_lower and "45" in ans_lower:
                    score += 1.0
                    feedback.append("Correctly identified 40-45 highest class.")
                if "less than" in ans_lower or "mean < median" in ans_lower:
                    score += 1.0
                    feedback.append("Correctly identified mean is less than median.")
                    
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Shape: skewed left, class: 40-45, mean is less than median."
                return score, 3, " | ".join(feedback)
                
        elif q_no == 3:
            if sub_no == 'a': # is.na() to count NA in Waste, returns 2 [2 marks]
                score = 0.0
                feedback = []
                if "sum(is.na(bakery_data$Waste))" in normalized_student or "sum(is.na(bakery_data[,'Waste']))" in normalized_student:
                    score += 1.0
                    feedback.append("Correct R command: sum(is.na(bakery_data$Waste)).")
                ans_lower = student_ans.lower()
                if "2" in ans_lower:
                    score += 1.0
                    feedback.append("Correct count value (2).")
                
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: sum(is.na(bakery_data$Waste)) and returns 2."
                return score, 2, " | ".join(feedback)
                
            elif sub_no == 'b': # na.omit behavior [3 marks]
                score = 0.0
                feedback = []
                ans_lower = student_ans.lower()
                if "remove" in ans_lower and ("na" in ans_lower or "row" in ans_lower or "missing" in ans_lower):
                    score += 1.0
                    feedback.append("Correctly explained na.omit removes rows with missing values.")
                if "baguette" in ans_lower and "donut" in ans_lower and "muffin" in ans_lower:
                    score += 1.0
                    feedback.append("Correctly listed remaining products (Baguette, Donut, Muffin).")
                if "lost" in ans_lower or "lose" in ans_lower or "problem" in ans_lower or "croissant" in ans_lower or "roti" in ans_lower:
                    score += 1.0
                    feedback.append("Explained the problem of losing valid data in other columns.")
                
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Explain that it removes any rows with NA, leaving Baguette, Donut, and Muffin, which wastes other valid data."
                return score, 3, " | ".join(feedback)
                
            elif sub_no == 'c': # mutate Revenue [2 marks]
                if "mutate(Revenue=Sold*Price_RM)" in normalized_student:
                    return 2.0, 2, "Correct mutate calculation."
                elif "mutate" in normalized_student and "Revenue" in normalized_student:
                    return 1.0, 2, "Mutate is used, but mathematical expression has syntax issues."
                return 0.0, 2, "Incorrect. Expected: bakery_data <- bakery_data %>% mutate(Revenue = Sold * Price_RM)"
                
            elif sub_no == 'd': # group_by Type and sum [3 marks]
                score = 0.0
                feedback = []
                if "group_by(Type)" in normalized_student:
                    score += 1.5
                    feedback.append("Correct group_by(Type).")
                if "summarise(Total_Sold=sum(Sold))" in normalized_student or "summarize(Total_Sold=sum(Sold))" in normalized_student:
                    score += 1.5
                    feedback.append("Correct summarise(Total_Sold = sum(Sold)).")
                elif "summarise" in normalized_student or "summarize" in normalized_student:
                    score += 0.5
                    feedback.append("Used summarise but calculation is wrong.")
                    
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: type_summary <- bakery_data %>% group_by(Type) %>% summarise(Total_Sold = sum(Sold))"
                return score, 3, " | ".join(feedback)

    # ==================== PRACTICE SET 4 ====================
    elif set_idx == 4:
        if q_no == 1:
            if sub_no == 'a': # read.csv vs read_csv difference [2 marks]
                score = 0.0
                feedback = []
                ans_lower = student_ans.lower()
                diffs = [
                    ('tibble', ['tibble', 'read_csv returns a tibble']),
                    ('speed', ['speed', 'faster', 'performance']),
                    ('package', ['package', 'readr', 'base']),
                    ('factors', ['factor', 'string', 'stringsasfactors']),
                ]
                for diff_name, keywords in diffs:
                    if any(kw in ans_lower for kw in keywords):
                        score += 1.0
                        feedback.append(diff_name.capitalize())
                        if score == 2.0:
                            break
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected differences: read_csv returns tibble, is faster, does not convert strings to factors, or requires readr."
                return score, 2, f"Correct difference noted: {', '.join(feedback)}"
                
            elif sub_no == 'b': # read_dta haven [1 mark]
                if "library(haven)" in normalized_student or "library('haven')" in normalized_student:
                    # accept with library or just read_dta
                    pass
                if "read_dta('supplier.dta')" in normalized_student:
                    return 1.0, 1, "Correct read_dta call."
                return 0.0, 1, "Incorrect. Expected: library(haven); read_dta('supplier.dta')"
                
            elif sub_no == 'c': # read_excel sheet Stock2026 [2 marks]
                score = 0.0
                feedback = []
                if "library(readxl)" in normalized_student or "library('readxl')" in normalized_student:
                    score += 1.0
                    feedback.append("Loaded library(readxl).")
                if "read_excel('inventory.xlsx',sheet='Stock2026')" in normalized_student:
                    score += 1.0
                    feedback.append("Correct read_excel syntax and sheet name.")
                elif "read_excel('inventory.xlsx'" in normalized_student:
                    score += 0.5
                    feedback.append("Correct function call but sheet name is missing or wrong.")
                    
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: library(readxl); read_excel('inventory.xlsx', sheet = 'Stock2026')"
                return score, 2, " | ".join(feedback)
                
        elif q_no == 2:
            if sub_no == 'a': # bar chart with position=fill [4 marks]
                score = 0.0
                feedback = []
                if "ggplot(gadget_data,aes(x=Brand,fill=Warranty))" in normalized_student:
                    score += 2.0
                    feedback.append("Correct base mappings x=Brand, fill=Warranty.")
                if "geom_bar(position='stack')" in normalized_student or "geom_bar()" in normalized_student:
                    score += 1.0
                    feedback.append("geom_bar with stack/default position.")
                ans_lower = student_ans.lower()
                if "position='fill'" in normalized_student or "position=\"fill\"" in student_ans or "fill" in ans_lower and "proportion" in ans_lower:
                    score += 1.0
                    feedback.append("Correctly noted geom_bar(position = 'fill') is used for proportions.")
                
                if score == 0.0:
                    return 0.0, 4, "Incorrect. Expected: ggplot(gadget_data, aes(x = Brand, fill = Warranty)) + geom_bar(position = 'stack') and use position = 'fill' for proportions."
                return score, 4, " | ".join(feedback)
                
            elif sub_no == 'b': # line chart with point markers [3 marks]
                score = 0.0
                feedback = []
                if "ggplot(web_data,aes(x=Month,y=Visits))" in normalized_student:
                    score += 1.0
                    feedback.append("Correct base mapping.")
                if "geom_line()" in normalized_student:
                    score += 1.0
                    feedback.append("Added geom_line() layer.")
                if "geom_point()" in normalized_student:
                    score += 1.0
                    feedback.append("Added geom_point() layer.")
                    
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: ggplot(web_data, aes(x = Month, y = Visits)) + geom_line() + geom_point()"
                return score, 3, " | ".join(feedback)
                
            elif sub_no == 'c': # boxplot Brand Price_RM [3 marks]
                score = 0.0
                feedback = []
                if "ggplot(gadget_data,aes(x=Brand,y=Price_RM))" in normalized_student or "ggplot(gadget_data,aes(y=Price_RM,x=Brand))" in normalized_student:
                    score += 2.0
                    feedback.append("Correct base mapping x=Brand, y=Price_RM.")
                if "geom_boxplot()" in normalized_student:
                    score += 1.0
                    feedback.append("Added geom_boxplot() layer.")
                    
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: ggplot(gadget_data, aes(x = Brand, y = Price_RM)) + geom_boxplot()"
                return score, 3, " | ".join(feedback)
                
        elif q_no == 3:
            if sub_no == 'a': # select and filter >= 45 [3 marks]
                score = 0.0
                feedback = []
                if "select(Model,Units_Sold)" in normalized_student:
                    score += 1.0
                    feedback.append("Correct select columns.")
                if "filter(Units_Sold>=45)" in normalized_student:
                    score += 1.0
                    feedback.append("Correct filter >= 45 condition.")
                if "hot_models=" in normalized_student:
                    score += 1.0
                    feedback.append("Assigned to hot_models.")
                    
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: hot_models <- phone_data %>% select(Model, Units_Sold) %>% filter(Units_Sold >= 45)"
                return score, 3, " | ".join(feedback)
                
            elif sub_no == 'b': # arrange descending units sold [2 marks]
                score = 0.0
                feedback = []
                if "model_rank=phone_data" in normalized_student:
                    score += 0.5
                    feedback.append("Assigned to model_rank.")
                if "arrange(desc(Units_Sold))" in normalized_student or "arrange(-Units_Sold)" in normalized_student:
                    score += 1.5
                    feedback.append("Correct arrange descending.")
                elif "arrange(Units_Sold)" in normalized_student:
                    score += 0.5
                    feedback.append("Sorted ascending instead of descending.")
                    
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: model_rank <- phone_data %>% arrange(desc(Units_Sold))"
                return score, 2, " | ".join(feedback)
                
            elif sub_no == 'c': # rename Price_RM [2 marks]
                score = 0.0
                feedback = []
                if "phone_renamed=phone_data" in normalized_student:
                    score += 0.5
                    feedback.append("Assigned to phone_renamed.")
                if "rename(Retail_Price=Price_RM)" in normalized_student:
                    score += 1.5
                    feedback.append("Correct rename syntax (NewName = OldName).")
                elif "rename(Price_RM=Retail_Price)" in normalized_student:
                    score += 0.5
                    feedback.append("Rename argument order incorrect (OldName = NewName instead of NewName = OldName).")
                    
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected: phone_renamed <- phone_data %>% rename(Retail_Price = Price_RM)"
                return score, 2, " | ".join(feedback)
                
            elif sub_no == 'd': # full dplyr chain [3 marks]
                score = 0.0
                feedback = []
                if "mutate(Revenue=Units_Sold*Price_RM)" in normalized_student:
                    score += 1.0
                    feedback.append("Correct mutate(Revenue = Units_Sold * Price_RM).")
                if "group_by(Brand)" in normalized_student:
                    score += 1.0
                    feedback.append("Correct group_by(Brand).")
                if "summarise(Avg_Revenue=mean(Revenue))" in normalized_student or "summarize(Avg_Revenue=mean(Revenue))" in normalized_student:
                    score += 1.0
                    feedback.append("Correct summarise(Avg_Revenue = mean(Revenue)).")
                    
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: brand_summary <- phone_data %>% mutate(Revenue = Units_Sold * Price_RM) %>% group_by(Brand) %>% summarise(Avg_Revenue = mean(Revenue))"
                return score, 3, " | ".join(feedback)

    # ==================== PRACTICE SET 5 ====================
    elif set_idx == 5:
        if q_no == 1:
            if sub_no == 'a': # league_data <- read.csv("league_results.csv") [2 marks]
                if "league_data=read.csv('league_results.csv')" in normalized_student:
                    return 2.0, 2, "Correct read.csv call and assignment."
                elif "read.csv('league_results.csv')" in normalized_student:
                    return 1.0, 2, "Correct read.csv syntax but missing assignment to league_data."
                return 0.0, 2, "Incorrect. Expected: league_data <- read.csv('league_results.csv')"
                
            elif sub_no == 'b': # state TWO functions to inspect [2 marks]
                score = 0.0
                feedback = []
                ans_lower = student_ans.lower()
                inspect_funcs = ['head', 'str', 'glimpse', 'summary', 'view', 'dim', 'nrow', 'ncol']
                matched = 0
                for f in inspect_funcs:
                    if f in ans_lower:
                        matched += 1
                        feedback.append(f + "()")
                        score += 1.0
                        if matched == 2:
                            break
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Expected functions: head(), str(), glimpse(), summary(), View(), dim()."
                return score, 2, f"Correct functions identified: {', '.join(feedback)}"
                
            elif sub_no == 'c': # CSV advantage [1 mark]
                ans_lower = student_ans.lower()
                if "plain text" in ans_lower or "small" in ans_lower or "simple" in ans_lower or "universal" in ans_lower or "compatibility" in ans_lower or "software" in ans_lower or "version" in ans_lower or "open" in ans_lower:
                    return 1.0, 1, "Correct. CSV is a universal plain-text format compatible with almost all software."
                return 0.0, 1, "Incorrect. Mention plain text readability, software independence, or small file sizes."
                
        elif q_no == 2:
            if sub_no == 'a': # bar chart matches Division [3 marks]
                score = 0.0
                feedback = []
                if "ggplot(futsal_data,aes(x=Division))" in normalized_student:
                    score += 1.5
                    feedback.append("Correct base mapping x=Division.")
                if "geom_bar()" in normalized_student:
                    score += 1.5
                    feedback.append("Correct geom_bar() layer.")
                    
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: ggplot(futsal_data, aes(x = Division)) + geom_bar()"
                return score, 3, " | ".join(feedback)
                
            elif sub_no == 'b': # boxplot Match_Rating teams [4 marks]
                score = 0.0
                feedback = []
                if "ggplot(futsal_data,aes(x=Team,y=Match_Rating" in normalized_student or "ggplot(futsal_data,aes(y=Match_Rating,x=Team" in normalized_student:
                    score += 1.5
                    feedback.append("Correct base mappings x=Team, y=Match_Rating.")
                if "fill=Team" in normalized_student or "color=Team" in normalized_student:
                    score += 0.5
                    feedback.append("Added aesthetic color coloring per team.")
                if "geom_boxplot()" in normalized_student:
                    score += 1.0
                    feedback.append("Correct geom_boxplot() layer.")
                if "labs(" in normalized_student:
                    score += 1.0
                    feedback.append("Added titles and labels.")
                    
                if score == 0.0:
                    return 0.0, 4, "Incorrect. Expected: ggplot(futsal_data, aes(x = Team, y = Match_Rating, fill = Team)) + geom_boxplot() + labs(...)"
                return score, 4, " | ".join(feedback)
                
            elif sub_no == 'c': # boxplot interpretation [3 marks]
                score = 0.0
                feedback = []
                ans_lower = student_ans.lower()
                if "7.5" in ans_lower and "6.0" in ans_lower or "falcons" in ans_lower and "titans" in ans_lower and ("7" in ans_lower or "6" in ans_lower):
                    score += 1.0
                    feedback.append("Correct medians identified (Falcons ~7.5, Titans ~6.0).")
                if "falcons" in ans_lower and ("consistent" in ans_lower or "smaller" in ans_lower or "spread" in ans_lower):
                    score += 1.0
                    feedback.append("Correctly identified Falcons are more consistent (smaller spread).")
                if "outlier" in ans_lower and ("falcons" in ans_lower or "low" in ans_lower or "2" in ans_lower):
                    score += 1.0
                    feedback.append("Correctly commented on Falcons' outlier rating of ~2.")
                    
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Medians: Falcons 7.5, Titans 6.0; Falcons is more consistent; Falcons has an outlier rating of 2."
                return score, 3, " | ".join(feedback)
                
        elif q_no == 3:
            if sub_no == 'a': # average Goals with na.rm=TRUE [3 marks]
                if "mean(player_stats$Goals,na.rm=TRUE)" in normalized_student or "mean(player_stats$Goals,na.rm=T)" in normalized_student:
                    return 3.0, 3, "Correct mean calculation with na.rm=TRUE."
                elif "mean(" in normalized_student and "Goals" in normalized_student:
                    return 1.5, 3, "Correct function but missing or incorrect na.rm argument."
                return 0.0, 3, "Incorrect. Expected: mean(player_stats$Goals, na.rm = TRUE)"
                
            elif sub_no == 'b': # replace NA with 0 [2 marks]
                score = 0.0
                feedback = []
                ans_lower = student_ans.lower()
                if "not appropriate" in ans_lower or "inappropriate" in ans_lower or "no" in ans_lower or "wrong" in ans_lower:
                    score += 1.0
                    feedback.append("Correctly concluded that this is not appropriate.")
                if "bias" in ans_lower or "lower" in ans_lower or "not 0" in ans_lower or "missing" in ans_lower or "not scored" in ans_lower or "exclude" in ans_lower:
                    score += 1.0
                    feedback.append("Correct reasoning: replacing NA with 0 biases/lowers averages incorrectly.")
                
                if score == 0.0:
                    return 0.0, 2, "Incorrect. Discuss why NA is missing data and replacing it with 0 is inappropriate because it artificially lowers averages."
                return score, 2, " | ".join(feedback)
                
            elif sub_no == 'c': # mutate Goals_per_Match [2 marks]
                if "mutate(Goals_per_Match=Goals/Matches)" in normalized_student:
                    return 2.0, 2, "Correct mutate calculation."
                elif "mutate" in normalized_student and "Goals_per_Match" in normalized_student:
                    return 1.0, 2, "Mutate is used but mathematical syntax is incorrect."
                return 0.0, 2, "Incorrect. Expected: player_stats <- player_stats %>% mutate(Goals_per_Match = Goals / Matches)"
                
            elif sub_no == 'd': # group_by Team and mean Goals [3 marks]
                score = 0.0
                feedback = []
                if "group_by(Team)" in normalized_student:
                    score += 1.5
                    feedback.append("Correct group_by(Team).")
                if "summarise(Avg_Goals=mean(Goals,na.rm=TRUE))" in normalized_student or "summarize(Avg_Goals=mean(Goals,na.rm=TRUE))" in normalized_student or "summarise(Avg_Goals=mean(Goals,na.rm=T))" in normalized_student or "summarize(Avg_Goals=mean(Goals,na.rm=T))" in normalized_student:
                    score += 1.5
                    feedback.append("Correct summarise(Avg_Goals = mean(Goals, na.rm = TRUE)).")
                elif "summarise" in normalized_student or "summarize" in normalized_student:
                    score += 0.5
                    feedback.append("Summarise function used, but mean arguments are wrong.")
                    
                if score == 0.0:
                    return 0.0, 3, "Incorrect. Expected: team_summary <- player_stats %>% group_by(Team) %>% summarise(Avg_Goals = mean(Goals, na.rm = TRUE))"
                return score, 3, " | ".join(feedback)

    # FALLBACK GRADER (if not matched above)
    # Check if student answer matches reference answer exactly
    try:
        ref_ans = get_reference_answer(set_idx, q_no, sub_no)
        norm_ref = normalize_r_code(ref_ans)
        if normalized_student == norm_ref:
            return float(max_marks), max_marks, "Correct (Exact match)."
    except:
        pass
        
    return 0.0, max_marks, "Incorrect. Review the reference answer."

def get_max_marks(set_idx, q_no, sub_no):
    """
    Returns the maximum marks for a subquestion.
    """
    # Simple hardcoded map of marks
    marks_map = {
        # Set 1
        (1, 1, 'a'): 2, (1, 1, 'b'): 1, (1, 1, 'c'): 2,
        (1, 2, 'a'): 4, (1, 2, 'b'): 3, (1, 2, 'c'): 3,
        (1, 3, 'a'): 3, (1, 3, 'b'): 2, (1, 3, 'c'): 2, (1, 3, 'd'): 3,
        # Set 2
        (2, 1, 'a'): 2, (2, 1, 'b'): 1, (2, 1, 'c'): 2,
        (2, 2, 'a'): 4, (2, 2, 'b'): 3, (2, 2, 'c'): 3,
        (2, 3, 'a'): 1, (2, 3, 'b'): 3, (2, 3, 'c'): 2, (2, 3, 'd'): 2, (2, 3, 'e'): 2,
        # Set 3
        (3, 1, 'a'): 2, (3, 1, 'b'): 1, (3, 1, 'c'): 2,
        (3, 2, 'a'): 4, (3, 2, 'b'): 3, (3, 2, 'c'): 3,
        (3, 3, 'a'): 2, (3, 3, 'b'): 3, (3, 3, 'c'): 2, (3, 3, 'd'): 3,
        # Set 4
        (4, 1, 'a'): 2, (4, 1, 'b'): 1, (4, 1, 'c'): 2,
        (4, 2, 'a'): 4, (4, 2, 'b'): 3, (4, 2, 'c'): 3,
        (4, 3, 'a'): 3, (4, 3, 'b'): 2, (4, 3, 'c'): 2, (4, 3, 'd'): 3,
        # Set 5
        (5, 1, 'a'): 2, (5, 1, 'b'): 2, (5, 1, 'c'): 1,
        (5, 2, 'a'): 3, (5, 2, 'b'): 4, (5, 2, 'c'): 3,
        (5, 3, 'a'): 3, (5, 3, 'b'): 2, (5, 3, 'c'): 2, (5, 3, 'd'): 3,
    }
    return marks_map.get((set_idx, q_no, sub_no), 2)

def get_reference_answer(set_idx, q_no, sub_no):
    # Hardcoded or dynamic ref answer retrieval
    # For speed and safety, we can look it up from practice_sets.json or hardcode a fallback
    pass
