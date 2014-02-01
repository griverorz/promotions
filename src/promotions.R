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
        method, constraints, ruler_ideology, from_within
from simp
group by iteration, rank, method, constraints, ruler_ideology, from_within")
dbDisconnect(con)

p <- ggplot(ideology, aes(x = iteration, y = ideology, colour = factor(rank)))
pq <- p + geom_line() +
  facet_grid(method + constraints ~ from_within) +
  scale_colour_discrete("Rank") +
  scale_y_continuous(limits = c(-1, 1)) +
  xlab("Iteration") +
  ylab("Ideology")

file <- "~/Documents/wip/promotions/txt/img/ideology.pdf"
ggsave(file, pq)

#################### DISTRIBUTION OF QUALITY ####################
con <- dbConnect(drv,
                 dbname = 'promotions')

simp <- dbSendQuery(con,
"select avg(QUALITY) AS QUALITY, ITERATION, RANK,
        METHOD, CONSTRAINTS, RULER_IDEOLOGY
from simp
group by ITERATION, RANK, METHOD, CONSTRAINTS, RULER_IDEOLOGY")

quality <- fetch(simp, -1)
dbDisconnect(con)

p <- ggplot(quality, aes(x = iteration, y = quality, colour = factor(rank)))
pq <- p + geom_line() +
  facet_grid(method ~ constraints) +
  scale_colour_discrete("Rank") +
  scale_y_continuous(limits = c(-1, 1)) +
  xlab("Iteration") +
  ylab("Ideology")

file <- "~/Documents/wip/promotions/txt/img/quality.pdf"
ggsave(file, pq)

#################### INDIVIDUAL TRAJECTORIES ####################
con <- dbConnect(drv,
                 dbname = 'promotions')

simp <- dbGetQuery(con,
        "select id, method, constraints
         from
             (select *, rank() over (partition by method, constraints 
                                     order by random()) as rrank
              from simp
              where rank = 4 and iteration > 20)
         subquery
         where rrank = 1;")

full <- dbSendQuery(con, "select * from simp")
full <- fetch(full, -1)

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
  xlab("Iteration") +
  ylab("Rank")
