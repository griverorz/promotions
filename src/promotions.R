# data analysis from the simulation of promotion systems
# @griverorz
# 2Mar2012

library(ggplot2)
library(reshape)
library(plyr)
library(RPostgreSQL)
library(Hmisc)
theme_set(theme_bw())

wd <- "/Users/gonzalorivero/Documents/wip/promotions"
setwd(wd)

## ITERATION INTEGER,
## ID INTEGER,
## AGE INTEGER,
## RANK INTEGER,
## SENIORITY INTEGER,
## UNIT INTEGER,
## QUALITY DOUBLE PRECISION,
## IDEOLOGY DOUBLE PRECISION,
## METHOD VARCHAR,
## CONSTRAINTS VARCHAR,
## RULER_IDEOLOGY DOUBLE PRECISION;

#################### DISTRIBUTION OF IDEOLOGY ####################
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv,
                 dbname = 'promotions')

ideology <- dbGetQuery(con,
"select avg(ideology) as ideology, iteration, rank,
        constraints, ruler_ideology, from_within, 
        params_ideo, params_qual
from simp
group by iteration, rank, constraints, ruler_ideology, from_within, 
         params_ideo, params_qual;")
dbDisconnect(con)

p <- ggplot(ideology, aes(x = iteration, y = ideology, colour = factor(rank)))
pq <- p + geom_line() +
  facet_grid(constraints ~ from_within) +
  scale_colour_discrete("Rank") +
  scale_y_continuous(limits = c(-1, 1)) +
  xlab("Iteration") +
  ylab("Ideology")

file <- "~/Documents/wip/promotions/txt/img/ideology.pdf"
ggsave(file, pq)

#################### DISTRIBUTION OF QUALITY ####################
con <- dbConnect(drv,
                 dbname = 'promotions')

quality <- dbGetQuery(con,
"select avg(quality) as quality, iteration, rank,
        constraints, ruler_ideology, from_within,
        params_ideo, params_qual
from simp
group by iteration, rank, constraints, ruler_ideology, from_within, 
        params_ideo, params_qual;")
dbDisconnect(con)

p <- ggplot(quality, aes(x = iteration, y = quality, colour = factor(rank)))
pq <- p + geom_line() +
  facet_grid(constraints ~ from_within) +
  scale_colour_discrete("Rank") +
  scale_y_continuous(limits = c(-1, 1)) +
  xlab("Iteration") +
  ylab("Quality")

file <- "~/Documents/wip/promotions/txt/img/quality.pdf"
ggsave(file, pq)

#################### PARAMETERS ####################
con <- dbConnect(drv,
                 dbname = 'promotions')

params <- dbGetQuery(con,
"select avg(params_ideo) as pideo,
        avg(params_qual) as pqual,
        iteration,
        constraints, ruler_ideology, from_within
from simp
group by iteration, constraints, ruler_ideology, from_within
order by iteration;")
dbDisconnect(con)

p <- ggplot(params, aes(x = pideo, y = pqual))
pq <- p + geom_path() +
  facet_grid(constraints ~ from_within)


#################### INDIVIDUAL TRAJECTORIES ####################
con <- dbConnect(drv,
                 dbname = 'promotions')

simp <- dbGetQuery(con,
        "select id, method, constraints
         from
             (select *, rank() over (partition by method, constraints 
                                     order by random()) as rrank
              from simp
              where rank = 4 and iteration > 80)
         subquery
         where rrank = 1;")

full <- dbGetQuery(con, "select * from simp")

dbDisconnect(con)

generals <- vector("list", nrow(simp))
for (i in 1:nrow(simp)) {
    generals[[i]] <-
    full[full$id == simp$id[i] &
         full$method == simp$method[i] &
         full$constraints == simp$constraints[i], ]
}

## pick general to follow
generals <- do.call(rbind, generals)

p <- ggplot(generals, aes(x = age, y = rank))
pq <- p + geom_line() +
  geom_point(shape = 1) +
  facet_grid(constraints ~ method) +
  xlab("Age") +
  ylab("Rank")

#################### FACTIONS ####################
con <- dbConnect(drv,
                 dbname = 'promotions')

factions <- dbGetQuery(con,
"select count(distinct which_faction), iteration,
        constraints, from_within
from simp
where which_faction is not null
group by iteration, constraints, from_within;")
dbDisconnect(con)

p <- ggplot(factions, aes(x = iteration, y = count))
pq <- p + geom_line() +
  facet_grid(constraints ~ from_within) 
