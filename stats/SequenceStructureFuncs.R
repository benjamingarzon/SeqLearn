
# recursively find all paths from a certain node

find_paths = function(myindex, transitions, seq_size, pos = 0){
  s = subset(transitions, from == myindex)
  
  paths = list()
  
  if (nrow(s) > 0 & pos < seq_size){
    for (i in 1:nrow(s))
    {
      next_index = s["to"][i, ]
      
      mytransitions = transitions
      mytransitions = subset(mytransitions, !(from == myindex & to == next_index))
      mytransitions = subset(mytransitions, !(from == next_index & to == myindex))
      p = find_paths(next_index, mytransitions, seq_size, pos + 1)
      if(is.null(p))
        newpaths = list(next_index)
      else 
        newpaths = lapply(p, function(x) c(next_index, x))
      paths = c(paths, newpaths)
      
    } 
    return(paths)
  } else return(NULL)
}


# generate paths given transitions
generate_paths = function(chords, allowed_dist = c(3), seq_size){

    # distance between transitions
  distance = as.matrix(dist(chords, method = 'manhattan'))
  
  bindistance = 0*(distance) 
  bindistance[ distance %in% allowed_dist ] = 1
  print(distance)
  print(bindistance)
  
  colors = c(rep("red", 4), rep("blue", 6))
  
  # plot transitions
  gplot(max(distance)-distance, mode="mds", arrowhead.cex = 0, displaylabels=TRUE, vertex.col = colors, edge.lwd = distance)
  
  degrees = colSums(bindistance)
  print(degrees)
  transitions = melt(bindistance)
  colnames(transitions) = c("from", "to", "value")
  transitions = subset(transitions, value != 0)[-3]
  
  nchords = nrow(chords)
  paths = NULL
  
  for (index in 1:nchords)
    paths = c(paths, lapply(find_paths(index, transitions, seq_size, 1), function(x) c(index, x)))
  
  return(paths)
}



# select paths without cycles

select_path = function(path){
  for (i in seq(length(path))){
    segment = path[1:i]
    if (length(segment) == length(unique(segment))) maxi = i
  }
  return(path[1:maxi])
  
}


# transform chunk to binary

chunk_to_bin = function(mychunk, nchords)
{
  mymat = matrix(0, nchords, nchords)
  
  for (i in seq(length(mychunk)-1))
    mymat[mychunk[i], mychunk[i+1]] = 1
  
  return(as.vector(mymat))
  
}

# select paths with no cycles

select_unique = function(paths, seq_size){
  
  uniquepaths = lapply(paths, select_path)
  chunks = lapply(uniquepaths, function(x) x[1:min(seq_size, length(x))])
  lengths = sapply(chunks, length)
  maxchunks = unique(chunks[lengths == max(lengths)])
  
  return(maxchunks)
}


# number of different elements
chunkdist = function(x, y) length(x) - length(intersect(x, y))

# hamming distance considering transitions
get_vecdist = function(chunks, nchords){
  
  vecs = t(sapply(chunks, chunk_to_bin, nchords))
  vecdist = dist(vecs, method = 'manhattan')
  
}

# translate sequences
translate_seqs = function(chunks, chords){
  to_chords = function(x) paste(lapply(apply(chords[x, ] == 1, 1, which), paste, collapse = " "), collapse =" - ")
  lapply(chunks, to_chords)
}
