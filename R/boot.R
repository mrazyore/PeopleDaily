## Code sampel for bootstrapping
setwd('~/R')
library(readr)
eng_map=list()
code_map=list()
number_map=list()
chn<-read_lines("chn_country")
eng<-read_lines("eng_country")
codes<-read_lines("codes")
number<-read_lines("number")
for(i in 1:length(chn)){
  eng_map[chn[i]]<-eng[i]
  code_map[chn[i]]<-codes[i]
  number_map[chn[i]]<-number[i]
  
}

# loavg = c(read.csv('loavg.csv',header = FALSE))[[1]]
# losd = c(read.csv('losd.csv',header = FALSE))[[1]]
# hiavg = c(read.csv('hiavg.csv',header = FALSE))[[1]]
# hisd = c(read.csv('hisd.csv',header = FALSE))[[1]]
# estavg = c(read.csv('estavg.csv',header = FALSE))[[1]]
# estsd = c(read.csv('estsd.csv',header = FALSE))[[1]]
total.mean=15.38299
total.sd=13.72092

boot <- function(d, nsims) {
  result <- rep(NA, nsims)
  for (i in 1:nsims) {
    n <- dim(d)[1]
    id <- 1:n
    new.id <- sample(id, n, replace = TRUE)
    result[i] <- mean(d[new.id,])
    #if (i%%10==0) {cat(".")}
  }
  est <- mean(d[,]) ## estimate True value
  se <- sd(result) ## this is the bootstrapped standard error
  ci <- quantile(result, c(0.025, 0.975)) ## this is 95% confidence interval
  out <- list(est = est, se = se, ci = ci, lo=ci[[1]], hi=ci[[2]], result = result)
  
  return(out)
}



get.year<-function(s){
  year = strsplit(strsplit(s,'_')[[1]][2],'.',fixed = TRUE)[[1]][1]
  return(as.numeric(year))
}

nsims = 1000
countries =list.dirs(path = "./scores",recursive = FALSE)

avgest=c()

for(country in countries){
  if (length(dir(country))==0){
    next()
  }
  country.chnname = strsplit(country,'/')[[1]][3]
  country.name = eng_map[country.chnname][[1]]
  country.code = code_map[country.chnname][[1]]
  country.number = number_map[country.chnname][[1]]
  files = sort(list.files(path=country,pattern = "\\.csv"))

  files_path <- paste(country,files,sep = "/")
  freq_path <- paste('./percents/',country.chnname,'percent.csv',sep='')
  article.freq <-read.csv(freq_path,header = FALSE)[[1]]
  freq.max = max(article.freq)
  #article.freq<-article.freq/freq.max/4
  freq.year <-1946:2015
  
  pre.year<-get.year(files[1])-1
  
  year.c <-c()
  sd.c <- c()
  est.c <- c()
  lo.c <- c()
  hi.c <- c()
  
  year_list <-list()
  sd_list <- list()
  est_list <- list()
  lo_list <- list()
  hi_list <-list()
  ci_list <-list()
  result_list <- list()
    
  for (i in 1:length(files_path)){
    print(files[i])
    data = read.csv(files_path[i],header=FALSE)
    output <-boot(data,nsims)
    year<-get.year(files[i])
    
    avgest <- c(avgest,output[[1]])
    
    if(year==pre.year+1){
      year.c <- c(year.c,c(year))
      est.c <- c(est.c,((output[[1]]-total.mean))+50)
      sd.c <- c(sd.c,c(output[[2]]))
      lo.c <- c(lo.c,((output[[4]]-total.mean))+50)
      hi.c <-c(hi.c,((output[[5]]-total.mean))+50)
    }else{
      year_list<-c(year_list,list(year.c))
      sd_list <-c(sd_list,list(sd.c))
      est_list <- c(est_list,list(est.c))
      lo_list <- c(lo_list,list(lo.c))
      hi_list <-c(hi_list,list(hi.c))
      
      year.c <- c(year)
      est.c <- c(output[[1]])
      sd.c <- c(output[[2]])
      lo.c <- c(output[[4]])
      hi.c <- c(output[[5]])
    }
    pre.year<-year
    result_list <- c(result_list,list(output[[6]]))
    ci_list <-c(ci_list,list(output[[3]]))
    #print(result_list[i])
  }
  if(length(year.c)>0){
    year_list<-c(year_list,list(year.c))
    sd_list <-c(sd_list,list(sd.c))
    est_list <- c(est_list,list(est.c))
    lo_list <- c(lo_list,list(lo.c))
    hi_list <-c(hi_list,list(hi.c))
  }

  # do sth with the result
  if (!dir.exists('./plot')){
    dir.create('./plot')
  }
  image_path = paste('./plot/Sentiment_',country.number,country.code,'.pdf',sep="")
  pdf(image_path)
  plot(0,xlim=c(1946,2015),ylim=c(0,100), type="n",xlab="Year",ylab = "Sentiment",main = country.name[[1]])
  for (i in 1:length(hi_list)){
    temp.lo=lo_list[[i]]
    temp.hi=hi_list[[i]]
    temp.est=est_list[[i]]
    temp.year=year_list[[i]]
    
    # fill 0 into missing year artical freq
    if (i == 1) {
      pad_head = year_list[[i]][1]-1946
      article.freq = c(rep(0.0,pad_head),article.freq)
    }
    if (i < length(hi_list)) {
      temp_len = length(year_list[[i]])
      start_index = year_list[[i]][temp_len]-1946 + 1
      gap = year_list[[i+1]][1]-year_list[[i]][temp_len] - 1
      freq_len=length(article.freq)
      article.freq = c(article.freq[1:start_index],rep(0.0,gap),article.freq[(start_index+1):freq_len])
    }
    if (i == length(hi_list)) {
      temp_len = length(year_list[[i]])
      pad_end = 2015 - year_list[[i]][temp_len]
      article.freq = c(article.freq,rep(0.0,pad_end))
    }
    
    points.fill<-c(temp.lo,rev(temp.hi))
    #plot(c(temp.year,rev(temp.year)),points.fill,type='n', ylim=c(-40,100))
    polygon(c(temp.year,rev(temp.year)),points.fill,border=NA,col="gray")
    points(temp.year,temp.est,pch=20,col="blue",type='l')

  }
  
  abline(h=50,col="gray")
  par(new=TRUE)
  plot(article.freq~freq.year, type="h", ylim=c(0,1), xlab="",ylab="", xaxt="n",yaxt="n")
  
  
  dev.off()
}

# run first time to get total mean and sd
# and then run second time with mean and sd filled in
total.mean = mean(avgest)
total.sd = sd(avgest)

save.image()
