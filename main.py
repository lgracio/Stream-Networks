import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
from parameters import *



def main():
    for net in data.keys():
        if not data[net][0]:
            continue

        directed, preprocess_type, window_size, sample_fraction, filename = data[net][1:]

        network_file = preprocess(preprocess_type,filename)

        # Store network in memory.
        edges, vertices = [], []
        for line in network_file:
            node1, node2, timeStamp = line.split()

            # Skip self-loops
            if node1 == node2:
                continue

            vertices.append(int(node1))
            vertices.append(int(node2))
            edges.append((node1,node2,round(float(timeStamp))))

        close_network_file(network_file,preprocess_type)

        # Use successive ID's for vertices
        vertices = list(set(vertices))
        number_of_nodes = len(vertices)
        vertices.sort()
        vertex_map = {}
        for i in range(len(vertices)):
            vertex_map[vertices[i]] = i

        # Update the edges with the new ID's
        new_edges = []
        for node1,node2,timeStamp in edges:
            new_edges.append((str(vertex_map[int(node1)]),str(vertex_map[int(node2)]),timeStamp))

        # Sort the edges chronologically
        sorted_edges = sorted(new_edges, key=lambda tup: tup[2])

        # Normalize timestamps so that the first value is 0
        edges = [(node1,node2,timeStamp-sorted_edges[0][2]) for (node1,node2,timeStamp) in sorted_edges]

        # Sample the network
        edges = edges[:int(sample_fraction*len(edges))]
        last_timestamp = edges[-1][2]


        # Queue to compute timeout of edges
        edge_timout = []

        # Data structure to ignore multi-edges
        edge_exists = {}

        # Compute and store the initial state of the network (before updates)
        output_initial = open("Stream Networks/"+net+"_initial.edges",'w')
        output_initial.write("DIRECTED\n") if directed else output_initial.write("UNDIRECTED\n")
        output_initial.write("Nodes "+str(number_of_nodes)+'\n')


        while edges[0][2] < window_size:
            node1, node2, timeStamp = edges.pop(0)
            edge_timout.append((node1,node2,timeStamp+window_size))
            if verify_edge_NOTexists(edge_exists, directed, node1, node2):
                output_initial.write(node1+" "+node2+'\n')
                edge_exists[(node1,node2)] = True
        output_initial.close()
        size_initial_network = len(edge_timout)

        # Store the edge distribution throughout the stream
        cur_edges = size_initial_network
        edge_distribution = [cur_edges]
        time_distribution = [timeStamp]

        # Compute and store the edge updates
        output_stream = open("Stream Networks/"+net+"_stream.edges",'w')
        n_additions = 0
        n_deletions = 0


        while edges:
            node1, node2, timeStamp = edges.pop(0)

            while edge_timout and edge_timout[0][2] < timeStamp:
                n1, n2, t = edge_timout.pop(0)
                if not verify_edge_NOTexists(edge_exists, directed, n1, n2):
                    output_stream.write("R "+str(n1)+" "+str(n2)+'\n')
                    edge_exists[(n1,n2)] = False
                    n_deletions += 1
                    cur_edges -= 1
                    edge_distribution.append(cur_edges)
                    time_distribution.append(t)

            if verify_edge_NOTexists(edge_exists, directed, node1, node2):
                output_stream.write("A "+str(node1)+" "+str(node2)+'\n')
                edge_exists[(node1,node2)] = True
                n_additions += 1
                cur_edges += 1
                edge_distribution.append(cur_edges)
                time_distribution.append(timeStamp)
                edge_timout.append((node1,node2,timeStamp+window_size))
        output_stream.close()


        # Create a file with some meta information
        output_meta = open("Stream Networks/"+net+"_meta.txt",'w')
        string = "Network: "+net+"\nNumber of edges in the initial network: "+str(size_initial_network)+\
                 "\nNumber of edge additions: "+ str(n_additions)+"\nNumber of edge deletions: "+str(n_deletions)+\
                 "\nNumber of edges not deleted: "+str(len(edge_timout))+"\nLast timestamp: "+str(last_timestamp)+\
            "\nTotal number of nodes: "+str(number_of_nodes)+"\nAverage number of edges: "\
                 +str(round(sum(edge_distribution)/len(edge_distribution)))+"\nNumber of updates: "+\
                 str(n_additions+n_deletions)
        print(string)
        print("--------------------------------------------")
        output_meta.write(string)



        pdf = matplotlib.backends.backend_pdf.PdfPages("Edge Distributions/"+net+".pdf")
        # Plot the evolution of the number of edges after each update
        f = plt.figure()
        plt.plot(edge_distribution,'-')
        plt.title("Number of edges in the "+net+" network after each update \nSliding-window size: "+
                  str(round(window_size/SECONDS_IN_DAY,2))+" days, Sample fraction: "+str(sample_fraction))
        plt.xlabel("Update number")
        plt.ylabel("Number of edges")
        pdf.savefig(f)
        plt.close(f)

        # Plot the evolution of the number of edges as a function of time
        f = plt.figure()
        time_distribution = [x/SECONDS_IN_DAY for x in time_distribution]
        plt.plot(time_distribution,edge_distribution,'-')
        plt.title("Number of edges in the "+net+" network as a function of time\nSliding-window size: "+
                  str(round(window_size/SECONDS_IN_DAY,2))+" days, Sample fraction: "+str(sample_fraction))
        plt.xlabel("Time (days)")
        plt.ylabel("Number of edges")
        pdf.savefig(f)
        plt.close(f)

        pdf.close()


def verify_edge_NOTexists(edge_exists, directed, node1, node2):
    if directed:
        return ((node1,node2) not in edge_exists.keys()) or (not edge_exists[(node1,node2)])
    else:
        return (((node1,node2) not in edge_exists.keys()) or (not edge_exists[(node1,node2)])) and \
               (((node2,node1) not in edge_exists.keys()) or (not edge_exists[(node2,node1)]))



def preprocess(t, filename):

    if t == 0:
        return open(filename,'r')

    if t == 4:
        file = open(filename,'r',encoding="utf8")
        new_file = []
        skip = True
        for line in file:
            if not line:
                continue

            if line.split()[0] == "*Edges":
                skip = False
                continue
            if skip:
                continue

            line = line.split()
            node1, node2, frequency,day = line[0],line[1],line[2],line[3][1:-1]
            new_file.append((node1+" "+node2+" "+str(int(day)*SECONDS_IN_DAY)))

        return new_file



    if t == 3:
        file = open(filename,'r',encoding="utf8")
        new_file = []
        skip = True
        for line in file:
            if not line:
                continue
            if line.split()[0].strip() == "*arcs":
                skip = False
                continue
            if not skip:
                line = line.split()
                node1 = line[0]
                node2 = line[1]
                edges = line[2:]
                edge_string = ""
                for st in edges:
                    edge_string+=st
                edge_string = edge_string[2:-2]
                edges = edge_string.split('),(')
                for edge in edges:
                    edge = edge.split(',')
                    t1, t2 = int(edge[0]), int(edge[1])
                    for i in range(t1,t2):
                        timeStamp = t1*30*SECONDS_IN_DAY
                        new_file.append(node1+" "+node2+" "+str(timeStamp))
        return new_file

    if t == 2:
        file = open(filename,'r')
        new_file = []
        for line in file:
            node1, node2, timeStamp, tweetType = line.split()
            if tweetType == "RT":
                new_file.append(node1+" "+node2+" "+timeStamp)
        file.close()
        return new_file

    if t == 1:
        file = open(filename,'r')
        next(file)

        # Users and targets have repeated ID's. Here we make them distinct
        max_user_id = 0
        for line in file:
            a, user_id, c, d = line.split()
            max_user_id = max(max_user_id,int(user_id))
        file.close()

        new_file = []
        file = open(filename,'r')
        next(file)
        for line in file:
            discard, node1, node2, timeStamp = line.split()
            new_file.append(node1+" "+str(int(node2)+max_user_id+1)+" "+timeStamp)
        file.close()
        return new_file


def close_network_file(file, preprocess_type):
    if preprocess_type == 0:
        file.close()


if __name__ == "__main__":
    main()

