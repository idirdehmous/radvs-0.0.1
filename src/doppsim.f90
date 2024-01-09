        SUBROUTINE INTERPOLATE(LON,LAT,VRALT,
     &                         MLON,MLAT,
     &                         UGP,VGP,HGP,
     &                         NAZIMT,NDIST,
     &                         R1I,R1J,R2I,R2J,AI,AJ,
     &                         M1I,M1J,M2I,M2J,
     &                         UL,UI,UJ,
     &                         VL,VI,VJ,
     &                         HL,HI,HJ,
     &                         ZI,DI,ELANGLE,HEIGHT,NLEVEL,ANGLE,VRAD)
!SOUBROUTINE doppsim.f90
! THE SOUBROUTINE TAKES ALL NECESSARY ARRAYS FRM THE MAIN 
! PROGRAM RadVS.py AND LOOKS FOR THE NEAREST NEIGBORS IN 
! IN THE MODEL GRID POINTS SPACE 
! FROM A MODEL FORCAST FILE USING HDF5 RADAR  FILE
!  
! IN VERTICAL DIRECTION IT CALCULATES THE WIND SPEED
! BETWWEN TWO SECCESSIVE MODEL HEIGHTS BY LINEAR 
! INTERPOLATION 

!AUTHORS       : IDIR DEHMOUS  (ONM   --ALGERIA )
!              : FLORIAN MEIER (ZAMG  --AUSTRIA ) 
!LAST UPDATE   : 18-12-2018

         INTEGER,INTENT(IN) ::R1I,R1J,R2I,R2J,AI,AJ,M1I,M1J,M2I,M2J 
         INTEGER,INTENT(IN) ::UI,UJ,UL,VI,VJ,VL,HI,HJ,HL,ZI,DI
         INTEGER,INTENT(IN) ::NLEVEL
         REAL   ,INTENT(IN) ::ELANGLE ,HEIGHT
         REAL   ,INTENT(OUT)::ANGLE
         REAL , DIMENSION(R1I,R1J)   ,INTENT(IN) :: LON
         REAL , DIMENSION(R2I,R2J)   ,INTENT(IN) :: LAT
         REAL , DIMENSION(AI ,AJ )   ,INTENT(IN) :: VRALT
         REAL , DIMENSION(M1I,M1J)   ,INTENT(IN) :: MLON
         REAL , DIMENSION(M2I,M2J)   ,INTENT(IN) :: MLAT 
         REAL , DIMENSION(UL,UI,UJ)  ,INTENT(IN) :: UGP 
         REAL , DIMENSION(VL,VI,VJ)  ,INTENT(IN) :: VGP         
         REAL , DIMENSION(HL,HI,HJ)  ,INTENT(IN) :: HGP
         REAL , DIMENSION(ZI)        ,INTENT(IN) :: NAZIMT
         REAL , DIMENSION(DI)        ,INTENT(IN) :: NDIST
         
         INTEGER,DIMENSION(R1I)      :: I_ARM
         INTEGER,DIMENSION(R1J)      :: J_ARM
          
         REAL(kind=8) , DIMENSION(R1I,R1J),INTENT(OUT):: VRAD
         REAL(kind=8) , DIMENSION(R1I,R1J)    :: U ,V ,VH 
         REAL , PARAMETER :: PI = 3.1415927
         REAL , PARAMETER :: RE = 6371*1000.0
         REAL             :: PHI ,ALPHA ,DIFFALT
         REAL(KIND=8) :: A , B , C 
         INTEGER      :: M ,MK
         LOGICAL      :: LFLAG ! if TRUE beam hit the ground

!CF2PY   INTENT(IN) ::RI,RJ,MI,MJ,LON,LAT,MLON,MLAT


!        NAZIMT HAS THE SAME DIMENSION AS LON IN AXIS 0 
!        NDIST  HAS THE SAME DIMENSION AS LON IN AXIS 1     
     
         ANGLE= ELANGLE
         PHI=ELANGLE*PI/180.0
         RA = RE*(4./3.)


         DO I =1,R1I                 !AZIMUTES
           DO J =1,R1J                 !BINS
             dist2=900000.
             DO K =1,M1I                 !LAT MODEL GRID POINTS
               DO L =1,M1J                 !LON MODEL GRID POINTS
                 A=ABS(LON(I,J)-MLON(K,L))
                 B=ABS(LAT(I,J)-MLAT(K,L))
                 IF (A .LE. 2.E-2 .AND.  B .LE. 4.E-2) THEN            !FIND THE NEAREST GRID POINT
                  CALL SDIS(LAT(I,J),MLAT(K,L),LON(I,J),MLON(K,L),dist)
                   IF(dist<dist2)then
                     dist2=dist 
                     I_ARM(I) = K
                     J_ARM(J) = L
                   ENDIF
                 ENDIF 
               ENDDO
             ENDDO
           ENDDO
         ENDDO
         DO I=1,R1I
           DO J=1,R1J
         
        
 
             LFLAG=.FALSE.
             DO MK=2,NLEVEL
         
               DIFFALT=VRALT(I,J)-HGP(MK,I_ARM(I),J_ARM(J))
               IF (DIFFALT  .le. 0.0  .and. MK==2) THEN
                 LFLAG=.TRUE.
                 EXIT
               ELSEIF (DIFFALT  .le. 0.0) THEN
                 EXIT
               ENDIF
             ENDDO
             M=MK

             A=UGP(M,I_ARM(I),J_ARM(J))-UGP(M-1,I_ARM(I),J_ARM(J))
             B=HGP(M,I_ARM(I),J_ARM(J))-HGP(M-1,I_ARM(I),J_ARM(J))
             C=VGP(M,I_ARM(I),J_ARM(J))-VGP(M-1,I_ARM(I),J_ARM(J))

        
             U(I,J)= UGP(M,I_ARM(I),J_ARM(J))
     &     +(VRALT(I,J)-HGP(M,I_ARM(I),J_ARM(J)))*(A/B)

             V(I,J)= VGP(M,I_ARM(I),J_ARM(J))
     &     + (VRALT(I,J)-HGP(M,I_ARM(I),J_ARM(J)))*(C/B)

          IF(LFLAG)THEN
            U(I,J)= UGP(2,I_ARM(I),J_ARM(J))
            V(I,J)= VGP(2,I_ARM(I),J_ARM(J))
          ENDIF
          VH(I,J) = U(I,J)*SIN(NAZIMT(I))+V(I,J)*COS(NAZIMT(I))

          ALPHA=ATAN((NDIST(J)*COS(PHI))/(NDIST(J)*SIN(PHI)+RA+HEIGHT))
          VRAD(I,J)= VH(I,J)*COS(PHI + ALPHA)
!          IF(LFLAG) VRAD(I,J)=-999.99
!          write(*,*)U(I,J),UGP(M,I_ARM(I),J_ARM(J)),
!     &   UGP(M-1,I_ARM(I),J_ARM(J)),HGP(M,I_ARM(I),J_ARM(J)),
!     &   HGP(M-1,I_ARM(I),J_ARM(J)),VRALT(I,J),M
!         IF(VRAD(i,j)>60..or.VRAD(i,j)<-50.)THEN
          ! write(*,*) 'VRAD(i,j) , i , j,R1I,R1J',VRAD(i,j),i,j,R1I,
!     &   R1J 
          ! write(*,*)'U(I,J),V(I,J),I,J,M,VRALT(I,J)',U(I,J),V(I,J),
!     &   I,J,M,VRALT(I,J),HGP(I_ARM(I),J_ARM(J),M)
!         ENDIF
          ENDDO 
         ENDDO 

         write(*,*)'HORIZONTAL AND VERTICAL INTERPOLATION AT ELEVATION 
     & ANGLE :',    ELANGLE , 'DONE  !'
         END SUBROUTINE INTERPOLATE

         SUBROUTINE SDIS(zlat1,zlat2,zlon1,zlon2,zdistance)


         IMPLICIT NONE

         REAL,    INTENT(IN)    :: zlat2, zlon2, zlat1, zlon1
         REAL,    INTENT(INOUT) :: zdistance
         DOUBLE PRECISION                  :: degrad,ddhelp,ddlon1
         DOUBLE PRECISION                  :: ddlat2,ddlat1,ddlon2
         REAL :: RA=6378.135
         REAL , PARAMETER :: RPI = 3.1415927
         degrad=1.0*RPI/180.

         ddlat1=degrad*zlat1
         ddlat2=degrad*zlat2
         ddlon1=degrad*zlon1
         ddlon2=degrad*zlon2
         DDHELP=sin(DDLAT1)*sin(DDLAT2)+cos(DDLAT1)*cos(DDLAT2)*
     & cos((DDLON2-DDLON1))
         zdistance=RA*acos(DDHELP)

         RETURN


         END SUBROUTINE SDIS


