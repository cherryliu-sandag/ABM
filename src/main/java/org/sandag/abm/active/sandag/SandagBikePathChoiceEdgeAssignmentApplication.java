package org.sandag.abm.active.sandag;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.DecimalFormat;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

import org.apache.log4j.Logger;
import org.sandag.abm.active.*;
import org.sandag.abm.ctramp.*;

import com.pb.common.util.ResourceUtil;

public class SandagBikePathChoiceEdgeAssignmentApplication extends AbstractPathChoiceEdgeAssignmentApplication<SandagBikeNode,SandagBikeEdge,SandagBikeTraversal>
{
    private static final Logger logger = Logger.getLogger(SandagBikePathChoiceEdgeAssignmentApplication.class);
    private static final String BIKE_ASSIGNMENT_FILE_PROPERTY = "active.assignment.file.bike";
    
    List<Stop> stops;
    final static String[] TIME_PERIOD_LABELS = {"EA","AM","MD","PM","EV"};
    final static double[] TIME_PERIOD_BREAKS = {3,9,22,29,99};
    
    private ThreadLocal<SandagBikePathChoiceModel> model;
    
    public SandagBikePathChoiceEdgeAssignmentApplication(PathAlternativeListGenerationConfiguration<SandagBikeNode, SandagBikeEdge, SandagBikeTraversal> configuration, List<Stop> stops, final Map<String,String> propertyMap)
    {
        super(configuration);
        this.stops = stops;
        model = new ThreadLocal<SandagBikePathChoiceModel>() {
            @Override
            protected SandagBikePathChoiceModel initialValue() {
                return new SandagBikePathChoiceModel((HashMap<String,String>) propertyMap);
            }
        };
    }

    @Override
    protected Map<SandagBikeEdge, double[]> assignTrip(int tripNum,PathAlternativeList<SandagBikeNode, SandagBikeEdge> alternativeList)
    {
        Stop stop = stops.get(tripNum);
        Tour tour = stop.getTour();
        SandagBikePathAlternatives paths =  new SandagBikePathAlternatives(alternativeList);
        double[] probs = model.get().getPathProbabilities(tour.getPersonObject(), paths, stop.isInboundStop(), tour, false); 
        double numPersons = 1;
        if (tour.getPersonNumArray() != null && tour.getPersonNumArray().length > 1) {
            numPersons = tour.getPersonNumArray().length;
        }
        int periodIdx = findFirstIndexGreaterThan((double)stop.getStopPeriod(),TIME_PERIOD_BREAKS);
        
        Map<SandagBikeEdge, double[]> volumes = new HashMap<>();
        for (int pathIdx=0; pathIdx<probs.length; pathIdx++) {
            SandagBikeNode parent = null;
            for (SandagBikeNode node : alternativeList.get(pathIdx)) {
                if (parent != null) {
                    SandagBikeEdge edge = network.getEdge(parent,node);
                    double[] values;
                    if (volumes.containsKey(edge)) {
                        values = volumes.get(edge); 
                    } else {
                        values = new double[TIME_PERIOD_BREAKS.length];
                        Arrays.fill(values, 0.0);
                    }
                    values[periodIdx] += probs[pathIdx] * numPersons;
                    volumes.put(edge, values);
                }
                parent = node;
            }
        }
        
        return volumes;
    }

    @Override
    protected SandagBikeNode getOriginNode(int tripId)
    {
        return network.getNode(configuration.getOriginZonalCentroidIdMap().get(stops.get(tripId).getOrig()));
    }

    @Override
    protected SandagBikeNode getDestinationNode(int tripId)
    {
        return network.getNode(configuration.getDestinationZonalCentroidIdMap().get(stops.get(tripId).getDest()));
    }
    
    public static void main(String ... args) {
        if (args.length == 0) {
            logger.error( String.format("no properties file base name (without .properties extension) was specified as an argument.") );
            return;
        }
        logger.info("loading property file: " + ClassLoader.getSystemClassLoader().getResource(args[0] + ".properties").getFile().toString());
        
        if (args.length < 2) {
            logger.error( String.format("no sample rate was specified as an argument.") );
            return;
        }
        double sampleRate = Double.parseDouble(args[1]);
            
        //String RESOURCE_BUNDLE_NAME = "sandag_abm_active_test";
        @SuppressWarnings("unchecked") //this is ok - the map will be String->String
        Map<String,String> propertyMap = (Map<String,String>) ResourceUtil.getResourceBundleAsHashMap (args[0]);
        DecimalFormat formatter = new DecimalFormat("#.###");
        
        SandagBikeNetworkFactory factory = new SandagBikeNetworkFactory(propertyMap);
        Network<SandagBikeNode, SandagBikeEdge, SandagBikeTraversal> network = factory.createNetwork();
        
        PathAlternativeListGenerationConfiguration<SandagBikeNode,SandagBikeEdge,SandagBikeTraversal> configuration = new SandagBikeMgraPathAlternativeListGenerationConfiguration(propertyMap,network);
        
        BikeAssignmentTripReader reader = new BikeAssignmentTripReader(propertyMap);
        List<Stop> stops = reader.createTripList();
        
//        Map<Integer,AtomicInteger> tripsByTimePeriod = new TreeMap<>();
//        for (Stop stop : stops) {
//        	int period = ModelStructure.getSkimPeriodIndex(stop.getStopPeriod());
//        	if (!tripsByTimePeriod.containsKey(period))
//        		tripsByTimePeriod.put(period,new AtomicInteger(0));
//        	tripsByTimePeriod.get(period).incrementAndGet();
//        }
//        logger.info("|------------+------------|");
//        logger.info(String.format("| %10s | %10s |","period","trips"));
//        logger.info("|------------+------------|");
//        for (int period : tripsByTimePeriod.keySet())
//        	logger.info(String.format("| %10d | %10d |",period,tripsByTimePeriod.get(period).get()));
//        logger.info("|------------+------------|");
        
        Path outputDirectory = Paths.get(configuration.getOutputDirectory());
        Path outputFile = outputDirectory.resolve(propertyMap.get(BIKE_ASSIGNMENT_FILE_PROPERTY));
        SandagBikePathChoiceEdgeAssignmentApplication application = new SandagBikePathChoiceEdgeAssignmentApplication(configuration,stops,propertyMap);
        
        List<Integer> relevantTripNums = new ArrayList<>();
        for (int i=0; i<stops.size(); i++)
            relevantTripNums.add(i);
        
        Map<SandagBikeEdge,double[]> volumes = application.assignTrips(relevantTripNums);
        
        try {
            Files.createDirectories(outputDirectory);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        try (PrintWriter writer = new PrintWriter(outputFile.toFile())) {
            StringBuilder sb = new StringBuilder("a,b");
            for (String segment : TIME_PERIOD_LABELS)
                sb.append(",").append(segment);
            writer.println(sb.toString());
            Iterator<SandagBikeEdge> edgeIterator = network.edgeIterator();
            while (edgeIterator.hasNext()) {
                SandagBikeEdge edge = edgeIterator.next();
                sb = new StringBuilder();
                sb.append(edge.getFromNode().getId()).append(",").append(edge.getToNode().getId());
                if (volumes.containsKey(edge)) {
                    for (double value : volumes.get(edge))
                        sb.append(",").append(formatter.format(value/sampleRate));
                } else {
                    for (int i = 0; i<TIME_PERIOD_BREAKS.length; i++)
                        sb.append(",").append(formatter.format(0.0));
                }
                writer.println(sb.toString());
            }
        } catch (IOException e) {
            logger.fatal(e);
            throw new RuntimeException(e);
        }

    }
}
