# data analysis from the simulation of promotion systems
# @griverorz
# 2Mar2012

library(ggplot2)
library(reshape)
library(plyr)
library(Hmisc)
theme_set(theme_bw())

  # READ AND ORGANIZE DATA (FOR EACH METHOD)
wd <- "~/Dropbox/tese/promotions/data"
ruler <- as.numeric(read.csv("~/Dropbox/tese/promotions/data/ruler.csv", header = FALSE))

sim <- vector("list", 3)
i <- 1
for (method in c("random", "closest", "ablest")) {
  completeFiles <- grep(method, list.files(wd))
  filesList <- lapply(list.files(wd, full.names = TRUE)[completeFiles], read.csv)
  simtmp <- do.call("rbind", filesList)
  simtmp <- simtmp[(simtmp$ordered == "False" & simtmp$seniority == "True") == FALSE,]
  levels(simtmp$ordered) <- c("Unordered", "Ordered")
  levels(simtmp$seniority) <- c("No seniority", "Seniority")
  simtmp$method <- capitalize(as.character(simtmp$method))
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
  ideology[[i]] <- ddply(sim[[i]], c("it", "rank", "ordered", "seniority"), 
                         function(df) mean(df$ideology))
}

ideology <- do.call("rbind", ideology)
ideology$method <- rep(c("Random", "Closest", "Ablest"), each = nrow(ideology)/3)
names(ideology)[3] <- "orderprom"

p <- ggplot(ideology, aes(x = it, y = V1, colour = factor(rank)))
pq <- p + geom_line() + 
  facet_grid(seniority + orderprom ~ method) +
  scale_colour_discrete("Rank") +
  scale_y_continuous(limits = c(-1, 1)) +
  geom_hline(y = ruler, linetype = 3, alpha = .7) +
  xlab("Iteration") +
  ylab("Ideology") 
  ## opts(legend.position = "none")
file <- "~/Documents/tese/promotions/paper/figures/ideology.pdf"
ggsave(file, pq)

# DISTRIBUTION OF QUALITY

# Average quality by rank
## quality <- ddply(sim, c("it", "rank", "seniority", "method"), function(df) mean(df$quality))


# Total quality of the military (weighted by rank: weight is the actual rank 1-4) normalized by the maximum possible efficiency (all individuals with quality 1).
N <- table(sim[[1]]$it)[1]/2
maxE <- sum(sim[[1]][sim[[1]]$seniority == "Seniority" & sim[[1]]$ordered == "Ordered" & sim[[1]]$it == 1, "rank"])

efficiency <- vector("list", 3)
for (i in 1:3) {
  E <- sapply(split(sim[[i]], list(sim[[i]]$it, sim[[i]]$ordered, sim[[i]]$seniority, sim[[i]]$method)), function(x) sum(x$quality*x$rank*x$order))
  efficiency[[i]] <- E/maxE
}
efficiency <- do.call("c", efficiency)
# reshape the efficiency to a ggplot-friendy dataset
it_and_ind <- do.call("rbind", strsplit(names(efficiency), ".", fixed = TRUE))
it_and_ind <- as.data.frame(it_and_ind)
names(it_and_ind) <- c("it", "ordered", "seniority", "method")
eff <- data.frame("it" = as.numeric(as.character(it_and_ind$it)), "ordered" = it_and_ind$ordered, 
                  "seniority" = it_and_ind$seniority, "efficiency" = efficiency, "method" = capitalize(as.character(it_and_ind$method)))
senord <- paste(eff$ordered, eff$seniority)
eff <- eff[senord != "Unordered Seniority",]

p <- ggplot(eff, aes(x = it, y = efficiency, colour = factor(method)))
pq <- p + geom_line(colour = "black") + 
  facet_grid(seniority + ordered ~  method) +
  opts(legend.position = "none") +
  ## scale_colour_discrete("Rank") +
  ## scale_y_continuous(limits = c(0, 1)) +
  xlab("Iteration") +
  ylab("Efficiency")
file <- "~/Documents/tese/promotions/paper/figures/efficiency.pdf"
ggsave(file, pq)


# DISTRIBUTION OF UTILITY
utility <- vector("list", 3)
for (i in 1:3) {
  utility[[i]] <- ddply(sim[[i]], c("it", "rank", "ordered", "seniority", "method"), function(df) mean(df$utility))
}
utility <- do.call("rbind", utility)
sim_utility <- do.call("rbind", sim)

its <- seq(1, max(sim_utility$it), by = 50)
p <- ggplot(sim_utility[sim_utility$it %in% its,], aes(x = factor(it), y = utility))
pq <- p + geom_boxplot(aes(fill = factor(rank))) + 
  facet_grid(seniority + ordered ~ method) +
  scale_fill_discrete("Rank") +
  xlab("Iteration") +
  ylab("Utility")
file <- "~/Documents/tese/promotions/paper/figures/utility.pdf"
ggsave(file, pq)


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

### PLOT WEIGHTED QUALITY OF EACH INDIVIDUAL
sim <- do.call("rbind", sim)

p <- ggplot(sim, aes(x = it, y = wquality, colour = factor(rank)))
pq <- p + geom_point(alpha = .6, size = 1, shape = 4) + 
  facet_grid(seniority + ordered ~ method) +
  scale_colour_discrete("Rank") +
  xlab("Iteration") +
  ylab("Capacity")

# WEIGHTED UTILITY FOR EACH MILITARY MEN
sim$wutility <- sim$wquality*sim$utility

p <- ggplot(sim, aes(x = it, y = wutility, colour = factor(rank)))
pq <- p + geom_point(size = 1, shape = 1) + 
  facet_grid(ordered + seniority ~ method) +
  xlab("Iteration") +
  ylab("Weighted utility") 
## file <- paste("~/Documents/wip/promotions/paper/figures/weighted_utility.png")
## ggsave(file, pq)


# INDIVIDUAL TRAJECTORIES # SHOULD TAKE THE MOST SIMILAR POSSIBLE INDIVIDUALS
individuals <- sim[sim$it > 20 & sim$rank == 4,]
individuals$senord <- paste(individuals$seniority, individuals$ordered)
split_individuals <- split(individuals, list(individuals$method, individuals$senord))

random_row <- function(df) {
  return(df[sample(1:nrow(df), 1), ])
}

random_individual <- lapply(split_individuals, function(x) random_row(x)[, "id"])

individual_path <- list('numeric', 9)

for (i in 1:9) {
  individual_path[[i]] <- sim[sim$id == random_individual[[i]], ]
}

individual_path <- do.call("rbind", individual_path)

normalize <- function(x) {
  out <- (x - min(x))/(max(x) - min(x))
  return(out)
}

p <- ggplot(individual_path, aes(x = age, y = rank))
pq <- p + geom_line() +
  geom_point(aes(size = wquality), shape = 1) +
  facet_grid(seniority + ordered ~ method) +
  xlab("Iteration") +
  ylab("Weighted utility") 
## file <- paste("~/Documents/wip/promotions/paper/figures/evolution_risk.png")
## ggsave(file, pq)
