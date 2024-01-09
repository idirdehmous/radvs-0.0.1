# -*- coding: utf-8 -*-

"""
PYTHON MODULE
decodhdf5.py  : OPEN AND SCANS A GIVEN HDF5 OPERA-ODIM FILE , 
                GET THE  VALUES OF GLOBAL ATTRIBUTES IN THE FILE
                AND ATTRIBUTES OF 'where' , 'what' UNDER EACH DATASET
                  
                THE RETURNED VALUES ARE PASSED TO RadVS.py MAIN PROGRAM                   


__AUTHOR      : IDIR DEHMOUS
__INSTITUTION : ZAMG  (Zentralanstahlt fuer Meteorologie und Geodynamik),AUSTRIA
                ONM   (Office National de la Meteorologie ) ,ALGERIA
__E-MAIL      : eddiedehmous@gmail.com

LAST UPDATE   : 18-12-2018

"""
import os
import sys,getopt,string
import h5py
import argparse
import re 



def Radar_info(fid):
    """Searching informations about 
     Radar station coordinate and height    (  "where"   group)
     Additional info could be retrieved in  order to   identify 
     the radar station WMO id and the NODE name ("what" group )
     """
    height ,lat , lon = 0, 0, 0
    wmoid , node = ' ' , ' '
    groupid = fid['/']    
    for item in groupid.keys():
        if 'where' in item:
          height=fid['/where'].attrs['height']
          lat   =fid['/where'].attrs['lat']
          lon   =fid['/where'].attrs['lon']
        if 'what'  in item:
          source=fid['/what'].attrs['source']
          srce=source.split(',')
          try:
             wmoid=srce[0]
             node =srce[1]
          except:
             IndexError
             wmoid='None' 
             node='None'
          date=fid['/what'].attrs['date']
          time=fid['/what'].attrs['time']
    return lat , lon , height,wmoid ,node , date , time 


def Scan_nr(fid):
    """
    Simple function to count the number of 
    scans in the file """

    nscans = 0
    groupid = fid['/']
    for item in groupid.keys():
        if "dataset" in item:
           nscans = nscans + 1
    return nscans





def Datasets_attrib(fid):
    """
    Function to search about global attributes in 
    the opened HDF5 file 
    how , what and where in whole the file 
    and the how , where and what attributes for each dataset

    input   :  fid   index of the file opened by h5py interface
    
    output  :  
             name, first scan azimuth, elevation angles
             nrays , nbins , rscale , rstart for each dataset
    """
    groupid=fid['/']
    nscan  =Scan_nr(fid)     # Get the number of scans
    dict_nbins  ={}
    dict_nrays  ={}
    dict_elangle={}
    dsets  =[]
    a1gate =[]
    elangle=[]
    nbins  =[]
    nrays  =[]
    rscale =[]
    rstart =[]
    for n in range(1,nscan+1):
       path="/dataset%d" % n
       dsets.append(path)
       grpname = fid[path]
       a1gate.append(grpname['where'].attrs["a1gate"])
       elangle.append(grpname['where'].attrs["elangle"])
       rscale.append(grpname['where'].attrs["rscale"])
       rstart.append(grpname['where'].attrs["rstart"])
       nbins.append(grpname['where'].attrs["nbins"])
       nrays.append(grpname['where'].attrs["nrays"])

    return dsets,a1gate,elangle,nbins,nrays,rscale,rstart 




def Get_subgroup_attrib(fid , dataset):
    """   
    Function to look about  datasets and return 
    their global interinsic attributes if those are different 
    from the global ones
    input : fid file index and dataset path 
    output: dsets , a1gate, elangle, nbins ,nrays, rscale,rstart"""


# Looking for what, where and how  attributes in subgoups
    wt_att  ="what" 
    wr_att  ="where"
    hw_att  ="how"

#Listes
    prod   = []
    stdate = [] 
    sttime = [] 
    eddate = []
    edtime = []
    a1gate = []
    elangle= []   
    nbins  = []
    nrays  = []
    rscale = []
    rstart = []

# Additional attributes in how group if  existes
    rpm     =[]
    plswidth=[]
    vsamples=[]
    
    groupid = fid['/'+dataset]
    if wt_att in groupid.keys():
       if len(list(groupid[wt_att].attrs.keys())) != 0:
          prod.append(groupid[wt_att].attrs["product"])
          stdate.append(groupid[wt_att].attrs["startdate"])
          sttime.append(groupid[wt_att].attrs["starttime"])
          eddate.append(groupid[wt_att].attrs["enddate"])
          edtime.append(groupid[wt_att].attrs["endtime"])
       elif len(list(groupid.keys())) == 0:
          print 'Dataset :', dataset , ' has empty ',wt_att,' attribute' 
          pass 
    
           
    if wr_att in groupid.keys():
       if len(list(groupid[wr_att].attrs.keys())) != 0:
          a1gate.append(groupid[wr_att].attrs["a1gate"])
          elangle.append(groupid[wr_att].attrs["elangle"])
          nbins.append(groupid[wr_att].attrs["nbins"]  )
          nrays.append(groupid[wr_att].attrs["nrays"]  )
          rscale.append(groupid[wr_att].attrs["rscale"] )
          rstart.append(groupid[wr_att].attrs["rstart"] )
       elif len(list(groupid.keys())) == 0:
          pass 
          
          

    
    if hw_att in groupid.keys():
       if len(groupid[hw_att].attrs.keys()) != 0:
          rpm.append(groupid[hw_att].attrs["rpm"])
          plswidth.append(groupid[hw_att].attrs["pulsewidth"])
          vsamples.append(groupid[hw_att].attrs["Vsamples"])
          
         #  print 'Additional attributes are found in dataset :', dataset
         #  print 'Antenna revolution velocity                :', rpm
         #  print 'Antenna pulse width                        :', plswidth
       else:
          #print 'Dataset :', dataset , ' has empty ',hw_att ,' attribute' 
          pass 
    return  a1gate , elangle , nbins , nrays , rscale , rstart , stdate,sttime,eddate,edtime






# Get the data and their attribute for each data under dataset section 
def Get_data_attrib(fid , dataset):
    param=' '
# Store the data in the data_vl liste  
    data_vl=[]

# Get "where" group values
    gain    =[]
    nodata  =[]
    offset  =[]
    undet   =[]
    quantity=[]

    
# Get "how" group values
    starAZ =[]
    stopAZ =[]
    a1gate,elangle,nbins,nrays,rscale,rstart,stdate,sttime,eddate,edtime =Get_subgroup_attrib(fid , dataset ) 
    subgrp1   = fid['/'+dataset]
    i=0
    for grp in subgrp1:
        if re.match(r"data[0-9]+", grp ):
           i=i+1
           datagrp=  fid['/'+dataset+'/'+grp]
           if 'what' in datagrp.keys():
              gain.append(datagrp['/'+dataset+'/'+grp+'/what'].attrs["gain"])
              nodata.append(datagrp['/'+dataset+'/'+grp+'/what'].attrs["nodata"]) 
              offset.append(datagrp['/'+dataset+'/'+grp+'/what'].attrs["offset"])
              undet.append(datagrp['/'+dataset+'/'+grp+'/what'].attrs["undetect"])
              quantity.append(datagrp['/'+dataset+'/'+grp+'/what'].attrs["quantity"])
           else:
              #print 'No what group found for data in dataset :' , dataset       
              pass 
  
           if 'how'  in datagrp.keys():
              if len(datagrp['/'+dataset+'/'+grp+'/how'].attrs.values()) != 0:
                 try: 
                    starAZ.append(datagrp['/'+dataset+'/'+grp+'/how'].attrs["startazA"])  
                    stopAZ.append(datagrp['/'+dataset+'/'+grp+'/how'].attrs["stopazA"])
                 except:
                    KeyError  
                    starAZ.append('None')
                    stopAZ.append('None') 
              else:
                 #print 'how attribute in ', dataset+'/'+grp ,' is empty'
                 pass 
             
           else:
              pass 
              #print 'No how group found for data in dataset :' , dataset                 
 

        
           if 'data' in datagrp.keys(): 
              if 'quantity' in  datagrp['/'+dataset+'/'+grp+'/what'].attrs:
                 param=datagrp['/'+dataset+'/'+grp+'/what'].attrs['quantity']

              dim=datagrp['/'+dataset+'/'+grp+'/data'].value.shape
              data_vl.append(datagrp['/'+dataset+'/'+grp+'/data'].value)
              param=datagrp['/'+dataset+'/'+grp+'/what'].attrs['quantity']
              #print 'data%d' % i ,' found in dataset  :' ,dataset 
              #print 'Parameter found :                :' , param
              #print 'Data dimension                   :' ,dim 
              #print 'Elevation angle                  :' ,elangle
              #print 'Number of bins                   :' ,nbins
              #print 'Number of rays                   :' ,nrays 
              #print 'Radial resolution                :' ,rscale
           else:
              pass 
              #print 'No data  found  in dataset    :' , dataset
        
         
# Looking only for the VRAD data (Radial velocity )
    vrad_vals   =[]
    vrad_gain   =[]
    vrad_nodata =[]
    vrad_offset =[]
    vrad_nodetec=[]
    vrad_name =' ' 
    for grp in subgrp1:
        if re.match(r"data[0-9]+", grp ):
           i=i+1
           datagrp=  fid['/'+dataset+'/'+grp]
           if 'what' in datagrp.keys():
               param=datagrp['/'+dataset+'/'+grp+'/what'].attrs['quantity']
               if param=='VRAD':     
                  vrad_name=param
                  vrad_gain.append(datagrp['/'+dataset+'/'+grp+'/what'].attrs["gain"])
                  vrad_nodata.append(datagrp['/'+dataset+'/'+grp+'/what'].attrs["nodata"])
                  vrad_offset.append(datagrp['/'+dataset+'/'+grp+'/what'].attrs["offset"])
                  vrad_nodetec.append(datagrp['/'+dataset+'/'+grp+'/what'].attrs["undetect"])
                  vrad_vals.append(datagrp['/'+dataset+'/'+grp+'/data'].value)
   
    return  a1gate , elangle , nbins , nrays , rscale , rstart ,vrad_vals, vrad_gain , vrad_nodata, vrad_offset ,vrad_nodetec,vrad_name  


           


if __name__=='__main__':
   parser = argparse.ArgumentParser(argparse.RawTextHelpFormatter)
   parser.add_argument('-f'  ,'--file'     , help='Input filename in hdf5 format' , required=False)
   args   = parser.parse_args()
   filename =args.file
   print('decodehdf5.py is used as main program !')
   if args.file == None:
      print (parser.print_help())
      sys.exit(1)
   else:
      fid = h5py.File(filename, 'r')
      nscans=Scan_nr(fid)
      print(nscans)
      for i in range(1,nscans+1):
         Get_data_attrib(fid , '/dataset%d'  %  i)




