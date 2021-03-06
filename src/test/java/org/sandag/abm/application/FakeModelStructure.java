package org.sandag.abm.application;

import java.util.HashMap;
import org.sandag.abm.ctramp.ModelStructure;

public class FakeModelStructure
        extends ModelStructure
{

    @Override
    public HashMap<String, Integer> getWorkSegmentNameIndexMap()
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public HashMap<String, Integer> getSchoolSegmentNameIndexMap()
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public HashMap<Integer, String> getWorkSegmentIndexNameMap()
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public HashMap<Integer, String> getSchoolSegmentIndexNameMap()
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public String getWorkPurpose(int incomeCategory)
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public String getWorkPurpose(boolean isPtWorker, int incomeCategory)
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public String getUniversityPurpose()
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public String getSchoolPurpose(int age)
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public boolean getTourModeIsSov(int tourMode)
    {
        return tourMode == 1 ;
    }

    @Override
    public boolean getTourModeIsSovOrHov(int tourMode)
    {
        return (tourMode <=3);
    }

    @Override
    public boolean getTourModeIsS2(int tourMode)
    {
        // TODO Auto-generated method stub
        return tourMode==2;
    }

    @Override
    public boolean getTourModeIsS3(int tourMode)
    {
        // TODO Auto-generated method stub
        return tourMode==3;
    }

    @Override
    public boolean getTourModeIsHov(int tourMode)
    {
        return tourMode>=2 && tourMode<=3;
    }

    @Override
    public boolean getTourModeIsNonMotorized(int tourMode)
    {
        // TODO Auto-generated method stub
        return tourMode==4||tourMode==5;
    }

    @Override
    public boolean getTourModeIsBike(int tourMode)
    {
        return tourMode == 5;
    }

    @Override
    public boolean getTourModeIsWalk(int tourMode)
    {
        return tourMode==4;
    }

  
    @Override
    public boolean getTourModeIsTransit(int tourMode)
    {
        return tourMode>=6 && tourMode<=9;
    }

    @Override
    public boolean getTourModeIsWalkTransit(int tourMode)
    {
        return tourMode==6;
    }

    @Override
    public boolean getTourModeIsDriveTransit(int tourMode)
    {
        return tourMode==7||tourMode==8||tourMode==9;
    }

    @Override
    public boolean getTourModeIsPnr(int tourMode)
    {
        return tourMode==7;
    }

    @Override
    public boolean getTourModeIsKnr(int tourMode)
    {
        return tourMode==8;
    }

    @Override
    public boolean getTourModeIsTncTransit(int tourMode)
    {
        return tourMode==9;
    }
    @Override
    public boolean getTourModeIsMaas(int tourMode)
    {
        return tourMode==10||tourMode==11||tourMode==12;
    }

    
    @Override
    public boolean getTourModeIsSchoolBus(int tourMode)
    {
        return tourMode==13;
    }

    @Override
    public boolean getTripModeIsSovOrHov(int tripMode)
    {
        return getTourModeIsSovOrHov(tripMode);
    }

    @Override
    public boolean getTripModeIsTransit(int tripMode){
    	return getTripModeIsTransit(tripMode);
    }
    
    @Override
    public boolean getTripModeIsWalkTransit(int tripMode)
    {
        return getTripModeIsWalkTransit(tripMode);
    }

    @Override
    public boolean getTripModeIsPnrTransit(int tripMode)
    {
        return getTripModeIsPnrTransit(tripMode);
    }

    @Override
    public boolean getTripModeIsKnrTransit(int tripMode)
    {
        return getTripModeIsKnrTransit(tripMode);
    }

    @Override
    public boolean getTripModeIsS2(int tripMode)
    {
        return getTripModeIsS2(tripMode);
    }
    @Override
    public boolean getTripModeIsS3(int tripMode)
    {
        return getTripModeIsS3(tripMode);
    }

    @Override
    public double[][] getCdap6PlusProps()
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public int getDefaultAmPeriod()
    {
        // TODO Auto-generated method stub
        return 0;
    }

    @Override
    public int getDefaultPmPeriod()
    {
        // TODO Auto-generated method stub
        return 0;
    }

    @Override
    public int getDefaultMdPeriod()
    {
        // TODO Auto-generated method stub
        return 0;
    }

    @Override
    public int getMaxTourModeIndex()
    {
        // TODO Auto-generated method stub
        return 0;
    }

    @Override
    public String getModelPeriodLabel(int period)
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public int[] getSkimPeriodCombinationIndices()
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public int getSkimPeriodCombinationIndex(int startPeriod, int endPeriod)
    {
        // TODO Auto-generated method stub
        return 0;
    }

    @Override
    public String getSkimMatrixPeriodString(int period)
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public HashMap<String, HashMap<String, Integer>> getDcSizePurposeSegmentMap()
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public String[] getJtfAltLabels()
    {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public void setJtfAltLabels(String[] labels)
    {
        // TODO Auto-generated method stub

    }

}
