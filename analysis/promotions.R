# data analysis from the simulation of promotion systemsee
# @griverorz
# 2Mar2012

library(ggplot2)
library(reshape)
library(plyr)
library(Hmisc)
theme_set(theme_bw())

  # READ AND ORGANIZE DATA (FOR EACH METHOD)
wd <- "~/Dropbox/wip/promotions/data"
ruler <- as.numeric(read.csv("~/Dropbox/wip/promotions/data/ruler.csv", header = FALSE))

sim <- vector("list", 3)
i <- 1
for (method in c("random", "closest", "ablest")) {
  completeFiles <- grep(method, list.files(wd))
  filesList <- lapply(list.files(wd, full.names = TRUE)[completeFiles], read.csv)
  simtmp <- do.call("rbind", filesList)
  simtmp$ordered <- rep(c("False", "True"), each = nrow(simtmp)/2)
  simtmp$seniority <- rep(c("False", "True"), each = nrow(simtmp)/4)
  simtmp$method <- capitalize(method)
  sim[[i]] <- simtmp
  # recalculate utility for agents
  sim[[i]]$utility <- sim[[i]]$rank/sim[[i]]$age - abs(sim[[i]]$ideology - ruler)
  i <- i + 1
}

# CHECK INDIVIDUAL TRAJECTORY
# pick old member who is top rank
## out <- sim[as.numeric(names(total_promotions == 2)) & as.numeric(names(achieved_rank == 4)), ]
## candidates_plot <- sim[sim$age == 10 & sim$rank == 4 & sim$it > 50 & sim$method == "Ablest" & sim$seniority == "True", ]
## candidates_id <- sample(candidates_plot$id, 1)
## ex <- sim[sim$id == candidates_id, ]


# DISTRIBUTION OF IDEOLOGY
ideology <- vector("list", 3)
for (i in 1:3) {
  ideology[[i]] <- ddply(sim[[i]], c("it", "rank", "ordered", "seniority"), function(df) mean(df$ideology))
}

ideology <- do.call("rbind", ideology)
ideology$method <- rep(c("Random", "Closest", "Ablest"), each = nrow(ideology)/3)

p <- ggplot(ideology, aes(x = it, y = V1, colour = factor(rank)))
pq <- p + geom_line() + 
  facet_grid(ordered + seniority ~ method) +
  scale_colour_discrete("Rank") +
  scale_y_continuous(limits = c(-.9, .9)) +
  geom_hline(y = ruler, linetype = 3, alpha = .7) +
  xlab("Iteration") +
  ylab("Ideology") + 
  opts(legend.position = "none")
## file <- "~/Documents/wip/promotions/paper/figures/ideology.png"
## ggsave(file, pq, width = 7, height = 9)

# DISTRIBUTION OF QUALITY

# Average quality by rank
## quality <- ddply(sim, c("it", "rank", "seniority", "method"), function(df) mean(df$quality))


# Total quality of the military (weighted by rank: weight is the actual rank 1-4) normalized by the maximum possible efficiency (all individuals with quality 1).
N <- table(sim[[1]]$it)[1]/2
maxE <- sum(sim[[1]][sim[[1]]$seniority == "True" & sim[[1]]$it == 1, "rank"])

efficiency <- vector("list", 3)
for (i in 1:3) {
  E <- sapply(split(sim[[i]], list(sim[[i]]$it, sim[[i]]$seniority, sim[[i]]$method)), function(x) sum(x$quality*x$rank))
  efficiency[[i]] <- E/maxE
}
efficiency <- do.call("c", efficiency)
# reshape the efficiency to a ggplot-friendy dataset
it_and_ind <- do.call("rbind", strsplit(names(efficiency), ".", fixed = TRUE))
it_and_ind <- as.data.frame(it_and_ind)
names(it_and_ind) <- c("it", "seniority", "method")
eff <- data.frame("it" = as.numeric(as.character(it_and_ind$it)), "seniority" = it_and_ind$seniority, "efficiency" = efficiency, "method" = capitalize(as.character(it_and_ind$method)))

p <- ggplot(eff, aes(x = it, y = efficiency, colour = factor(method)))
pq <- p + geom_line() + 
  facet_grid(seniority ~  method) +
  scale_colour_discrete("Rank") +
  scale_y_continuous(limits = c(0, 1)) +
  xlab("Iteration") +
  ylab("Efficiency") + 
  opts(legend.position = "none")
file <- paste("~/Documents/wip/promotions/paper/figures/efficiency.png", sep = "")
ggsave(file, pq, width = 7, height = 5)


# DISTRIBUTION OF UTILITY
utility <- vector("list", 3)
for (i in 1:3) {
  utility[[i]] <- ddply(sim[[i]], c("it", "rank", "seniority", "method"), function(df) mean(df$utility))
}
utility <- do.call("rbind", utility)
utility_last <- subset(utility, it == 999)
sim_utility <- do.call("rbind", sim)

selected_it <- sim_utility$it
selected_it <- selected_it %% 100 == 0
p <- ggplot(sim_utility[selected_it,], aes(x = factor(it), y = utility))
pq <- p + geom_boxplot(aes(fill = factor(rank))) + 
  facet_grid(seniority ~ method) +
  scale_fill_discrete("Rank") +
  xlab("Iteration") +
  ylab("Utility")
file <- paste("~/Documents/wip/promotions/paper/figures/utility.png", sep = "")
ggsave(file, pq, width = 12, height = 5)


# COUP RISK ASSOCIATED WITH EACH MILITARY MEN 

# Measured by the quality of the army restricted to the children associated with officer i

is_children <- function(parent, children) {
  # given a parent unit, checks whether the unit children is a children or not
  parent_nchar <- nchar(parent)
  out <- ifelse(as.numeric(substr(children, 1, parent_nchar)) == parent, TRUE, FALSE) 
  return(out)
}


# THESE LINES HAVE BEEN RUN ON A DIFFERENT COMPUTER AND THE RESULT SAVED TO WQUALITY.RDATA
# the function has to be applied to a LOT of individuals so I divided the task into various batches
# First I create a dataset with children for each possible unit
nsoldiers <- table(sim[[1]]$it)[1]/2
whosfamily <- vector("list", nsoldiers)
for (i in 1:nsoldiers) {
  whosfamily[[i]] <- is_children(sim[[1]][i, "unit"], sim[[1]][sim[[1]]$it == sim[[1]]$it[i] & sim[[1]]$seniority == "False", "unit"])
  whosfamily[[i]] <- sim[[1]]$unit[1:nsoldiers][whosfamily[[i]]]
  names(whosfamily)[i] <- sim[[1]]$unit[i]
}

# Then I calculate the measure for everybody (without counting their children)
for (i in 1:3) {
  sim[[i]]$wquality <- sim[[i]]$rank*sim[[i]]$quality
}

# I then add the measure only for those individual who actually have children (no-soldiers)

for (k in 1:3) {
  officers <- seq(1, nrow(sim[[k]]))[nchar(sim[[k]]$unit) < nchar(max(sim[[k]]$unit))] #????
  for (i in officers) {
                                        # This loop takes a while. Seat back and relax
    ss <- whosfamily[[as.character(sim[[k]]$unit[i])]]
    ss <- sim[[k]]$unit %in% ss & sim[[k]]$it == sim[[k]]$it[i] & sim[[k]]$seniority == sim[[k]]$seniority[i]
    sim[[k]]$wquality[i] <- sum(sim[[k]][ss, "rank"]*sim[[k]][ss, "quality"])
  }
}

sim <- do.call("rbind", sim)

# TEST ALLOCATIONS
## lowqgenerals <- sim[sim$rank == 4 & sim$wquality < 10,]
##                                         # Take one example
## testunit <- lowqgenerals[1, "unit"]
## testit <- lowqgenerals[1, "it"]
## testsen <- lowqgenerals[1, "seniority"]
## testmethod <- lowqgenerals[1, "method"]

## testchildren <- whosfamily[[as.character(testunit)]]
## ss <- sim[sim$unit %in% testchildren & sim$it == testit & sim$seniority == testsen & sim$method == testmethod , ]
## sum(ss$rank*ss$quality)

p <- ggplot(sim, aes(x = it, y = wquality, colour = factor(rank)))
pq <- p + geom_point(alpha = .6, size = 1, shape = 4) + 
  facet_grid(seniority ~ method) +
  scale_colour_discrete("Rank") +
  xlab("Iteration") +
  ylab("Capacity")

# WEIGHTED UTILITY FOR EACH MILITARY MEN
sim$wutility <- sim$wquality*sim$utility

p <- ggplot(sim, aes(x = it, y = wutility, colour = factor(rank)))
pq <- p + geom_point(size = 1, shape = 1) + 
  facet_grid(seniority ~ method) +
  xlab("Iteration") +
  ylab("Weighted utility") 
file <- paste("~/Documents/wip/promotions/paper/figures/weighted_utility.png")
ggsave(file, pq)


# INDIVIDUAL TRAJECTORIES # SHOULD TAKE THE MOST SIMILAR POSSIBLE INDIVIDUALS
individuals <- sim[sim$it > 10 & sim$rank == 4,]
split_individuals <- split(individuals, list(individuals$method, individuals$seniority))

random_row <- function(df) {
  return(df[sample(1:nrow(df), 1), ])
}

random_individual <- lapply(split_individuals, function(x) random_row(x)[, "id"])

individual_path <- list('numeric', 6)

for (i in 1:6) {
  individual_path[[i]] <- sim[sim$id == random_individual[[i]], ]
}

individual_path <- do.call("rbind", individual_path)

normalize <- function(x) {
  out <- (x - min(x))/(max(x) - min(x))
  return(out)
}

## p <- ggplot(individual_path, aes(x = age, y = rank))
## pq <- p + geom_line() +
##   geom_point(aes(size = 1- normalize(individual_path$wutility)), shape = 1) +
##   facet_grid(seniority ~ method) +
##   xlab("Iteration") +
##   ylab("Weighted utility") 
## file <- paste("~/Documents/wip/promotions/paper/figures/evolution_risk.png")
## ggsave(file, pq)
