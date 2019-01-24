data{
  int N; 
  int Nclus; 
  vector[N] x;
  vector[N] y;
  int cluster[N];
}


parameters{
  
  vector[3] mu_hyp;
  vector<lower = 0>[3] sigma_hyp;
  
  vector[Nclus] a_r;
  vector[Nclus] b_r;
  vector[Nclus] c_r;

  real<lower = 0> sigma;

}



transformed parameters{
  
  vector[Nclus] a;
  vector[Nclus] b;
  vector[Nclus] c;

  vector[N] m;
  
  a = mu_hyp[1] + sigma_hyp[1]*a_r;
  b = mu_hyp[2] + sigma_hyp[2]*b_r;
  c = mu_hyp[3] + sigma_hyp[3]*c_r;
  
  for(i in 1:N){
    m[i] = a[cluster[i]]*exp(-b[cluster[i]]*x[i]) + c[cluster[i]];
  }
  
}

model {
  
  y ~ normal(m, sigma);
    
  sigma ~ cauchy(0, 1000);

  mu_hyp[1] ~ normal(500, 1000);
  mu_hyp[2] ~ normal(0, 10);
  mu_hyp[3] ~ normal(400, 1000);
  
  sigma_hyp[1] ~ cauchy(0, 1000);
  sigma_hyp[2] ~ cauchy(0, 10);
  sigma_hyp[3] ~ cauchy(0, 1000);

  a_r ~ normal(0, 1);
  b_r ~ normal(0, 1);
  c_r ~ normal(0, 1);

} 
