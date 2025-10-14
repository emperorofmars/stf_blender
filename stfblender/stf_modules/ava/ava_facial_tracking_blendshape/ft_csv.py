
# Taken from https://docs.google.com/spreadsheets/d/118jo960co3Mgw8eREFVBsaJ7z0GtKNr52IB4Bz99VTA

# SRanipal	ARkit	"FACS Reduced (Quest Pro)"	Unified Expressions
ft_csv = """\
-	-	-	EyeLookOut
Eye_Left_Left	eyeLookOutLeft	Eyes_Look_Left_L	EyeLookOutLeft
Eye_Right_Right	eyeLookOutRight	Eyes_Look_Right_R	EyeLookOutRight
-	-	-	EyeLookIn
Eye_Left_Right	eyeLookInLeft	Eyes_Look_Right_L	EyeLookInLeft
Eye_Right_Left	eyeLookInRight	Eyes_Look_Left_R	EyeLookInRight
-	-	-	EyeLookUp
Eye_Left_Up	eyeLookUpLeft	Eyes_Look_Up_L	EyeLookUpLeft
Eye_Right_Up	eyeLookUpRight	Eyes_Look_Up_R	EyeLookUpRight
-	-	-	EyeLookDown
Eye_Left_Down	eyeLookDownLeft	Eyes_Look_Down_L	EyeLookDownLeft
Eye_Right_Down	eyeLookDownRight	Eyes_Look_Down_R	EyeLookDownRight
-	-	-	EyeClosed
Eye_Left_Blink	eyeBlinkLeft	Eyes_Closed_L	EyeClosedLeft
Eye_Right_Blink	eyeBlinkRight	Eyes_Closed_L	EyeClosedRight
-	-	-	EyeSquint
Eye_Left_squeeze	eyeSquintLeft	Lid_Tightener_L	EyeSquintLeft
Eye_Right_squeeze	eyeSquintRight	Lid_Tightener_R	EyeSquintRight
-	-	-	EyeClosedSquintCorrective
-	-	-	EyeClosedSquintCorrectiveLeft
-	-	-	EyeClosedSquintCorrectiveRight
-	-	-	EyeWide
Eye_Left_Wide	eyeWideLeft	Upper_Lid_Raiser_L	EyeWideLeft
Eye_Right_Wide	eyeWideRight	Upper_Lid_Raiser_R	EyeWideRight
-	-	-	EyeDilation
Eye_Left_Dilation	-	-	EyeDilationLeft
Eye_Right_Dilation	-	-	EyeDilationRight
-	-	-	EyeConstrict
Eye_Left_Constrict	-	-	EyeConstrictLeft
Eye_Right_Constrict	-	-	EyeConstrictRight
-	-	-	BrowDown
-	browDownLeft	Brow_Lowerer_L	BrowDownLeft
-	browDownRight	Brow_Lowerer_R	BrowDownRight
-	-	-	EyeClosedBrowDownCorrective
-	-	-	EyeClosedBrowDownCorrectiveLeft
-	-	-	EyeClosedBrowDownCorrectiveRight
-	-	-	BrowPinchLeft
-	-	-	BrowPinchRight
-	browDownLeft	Brow_Lowerer_L	BrowLowererLeft
-	browDownRight	Brow_Lowerer_R	BrowLowererRight
-	-	-	BrowUp
-	-	-	BrowUpLeft
-	-	-	BrowUpRight
-	browInnerUp	-	BrowInnerUp
-	-	Inner_Brow_Raiser_L	BrowInnerUpLeft
-	-	Inner_Brow_Raiser_R	BrowInnerUpRight
-	-	-	EyeClosedBrowInnerUpCorrective
-	-	-	EyeClosedBrowInnerUpCorrectiveLeft
-	-	-	EyeClosedBrowInnerUpCorrectiveRight
-	-	-	BrowOuterUp
-	browOuterUpLeft	Outer_Brow_Raiser_L	BrowOuterUpLeft
-	browOuterUpRight	Outer_Brow_Raiser_R	BrowOuterUpRight
-	-	-	EyeClosedBrowOuterUpCorrective
-	-	-	EyeClosedBrowOuterUpCorrectiveLeft
-	-	-	EyeClosedBrowOuterUpCorrectiveRight
-	-	-	NoseSneer
-	noseSneerLeft	Nose_Wrinkler_L	NoseSneerLeft
-	noseSneerRight	Nose_Wrinkler_R	NoseSneerRight
-	-	-	NasalDilation
-	-	-	NasalDilationLeft
-	-	-	NasalDilationRight
-	-	-	NasalConstrict
-	-	-	NasalConstrictLeft
-	-	-	NaseConstrictRight
-	-	-	CheekSquint
-	cheekSquintLeft	Cheek_Raiser_L	CheekSquintLeft
-	cheekSquintRight	Cheek_Raiser_R	CheekSquintRight
-	cheekPuff	-	CheekPuff
Cheek_Puff_Left	-	Cheek_Puff_L	CheekPuffLeft
Cheek_Puff_Right	-	Cheek_Puff_R	CheekPuffRight
Cheek_Suck	-	-	CheekSuck
-	-	Cheek_Suck_L	CheekSuckLeft
-	-	Cheek_Suck_R	CheekSuckRight
Jaw_Open	jawOpen	Jaw_Drop	JawOpen
Mouth_Ape_Shape	-	-	MouthApeShape
-	mouthClose	-	MouthClosed
-	-	Lip_Towards_LB	-
-	-	Lip_Towards_LT	-
-	-	Lip_Towards_RB	-
-	-	Lip_Towards_RT	-
Jaw_Left	jawLeft	Jaw_Sideways_Left	JawLeft
Jaw_Right	jawRight	Jaw_Sideways_Right	JawRight
Jaw_Forward	jawForward	Jaw_Thrust	JawForward
-	-	-	JawBackward
-	-	-	JawClench
-	-	-	JawMandibleRaise
Mouth_Upper_Inside	mouthRollUpper	-	LipSuckUpper
-	-	Lip_Suck_LT	LipSuckUpperLeft
-	-	Lip_Suck_RT	LipSuckUpperRight
Mouth_Lower_Inside	mouthRollLower	-	LipSuckLower
-	-	Lip_Suck_LB	LipSuckLowerLeft
-	-	Lip_Suck_RB	LipSuckLowerRight
-	-	-	LipSuckCorner
-	-	-	LipSuckCornerLeft
-	-	-	LipSuckCornerRight
Mouth_O_Shape	mouthFunnel	-	LipFunnel
Mouth_Upper_Overturn	-	-	LipFunnelUpper
-	-	Lip_Funneler_RT	LipFunnelUpperRight
-	-	Lip_Funneler_LT	LipFunnelUpperLeft
Mouth_Lower_Overturn	-	-	LipFunnelLower
-	-	Lip_Funneler_RB	LipFunnelLowerRight
-	-	Lip_Funneler_LB	LipFunnelLowerLeft
Mouth_Pout	mouthPucker	-	LipPucker
-	-	Lip_Pucker_L	LipPuckerLeft
-	-	Lip_Pucker_R	LipPuckerRight
-	-	-	MouthUpperUp
Mouth_Upper_UpLeft	mouthUpperUpLeft	Upper_Lip_Raiser_L	MouthUpperUpLeft
Mouth_Upper_UpRight	mouthUpperUpRight	Upper_Lip_Raiser_R	MouthUpperUpRight
-	-	-	MouthLowerDown
Mouth_Lower_DownLeft	mouthLowerDownLeft	Lower_Lip_Depressor_L	MouthLowerDownLeft
Mouth_Lower_DownRight	mouthLowerDownRight	Lower_Lip_Depressor_R	MouthLowerDownRight
			MouthUpperDeepen
			MouthUpperDeepenLeft
			MouthUpperDeepenRight
-	mouthLeft	Mouth_Left	MouthLeft
Mouth_Upper_Left	-	-	MouthUpperLeft
Mouth_Lower_Left	-	-	MouthLowerLeft
-	mouthRight	Mouth_Right	MouthRight
Mouth_Upper_Right	-	-	MouthUpperRight
Mouth_Lower_Right	-	-	MouthLowerRight
-	-	-	MouthCornerPull
Mouth_Smile_Left	mouthSmileLeft	Lip_Corner_Puller_L	MouthCornerPullLeft
Mouth_Smile_Right	mouthSmileRight	Lip_Corner_Puller_R	MouthCornerPullRight
-	-	-	MouthCorner
Mouth_Smile_Left	mouthSmileLeft	Lip_Corner_Puller_L	MouthCornerSlantLeft
Mouth_Smile_Right	mouthSmileRight	Lip_Corner_Puller_R	MouthCornerSlantRight
-	-	-	MouthSmile
Mouth_Smile_Left	mouthSmileLeft	Lip_Corner_Puller_L	MouthSmileLeft
Mouth_Smile_Right	mouthSmileRight	Lip_Corner_Puller_R	MouthSmileRight
-	-	-	MouthFrown
Mouth_Sad_Left	mouthFrownLeft	Lip_Corner_Depressor_L	MouthFrownLeft
Mouth_Sad_Right	mouthFrownRight	Lip_Corner_Depressor_R	MouthFrownRight
-	-	-	MouthStretch
-	mouthStretchLeft	Lip_Stretcher_L	MouthStretchLeft
-	mouthStretchRight	Lip_Stretcher_R	MouthStretchRight
-	-	-	MouthSad
Mouth_Sad_Left	mouthFrownLeft	Lip_Corner_Depressor_L	MouthSadLeft
Mouth_Sad_Right	mouthFrownRight	Lip_Corner_Depressor_R	MouthSadRight
-	-	-	MouthDimple
-	mouthDimpleLeft	Dimpler_L	MouthDimpleLeft
-	mouthDimpleRight	Dimpler_R	MouthDimpleRight
-	-	-	MouthRaiser
-	mouthShrugUpper	Chin_Raiser_T	MouthRaiserUpper
Mouth_Lower_Overlay	mouthShrugLower	Chin_Raiser_B	MouthRaiserLower
			MouthPress
-	mouthPressLeft	Lip_Pressor_L	MouthPressLeft
-	mouthPressRight	Lip_Pressor_R	MouthPressRight
			MouthTightener
-	-	Lip_Tightener_L	MouthTightenerLeft
-	-	Lip_Tightener_R	MouthTightenerRight
-	tongueOut	-	TongueOut
Tongue_LongStep1	-	-	TongueOutStep1
Tongue_LongStep2	-	-	TongueOutStep2
Tongue_Down	-	-	TongueDown
Tongue_Up	-	-	TongueUp
Tongue_Left	-	-	TongueLeft
Tongue_Right	-	-	TongueRight
Tongue_UpLeft_Morph	-	-	TongueUpLeftMorph
Tongue_UpRight_Morph	-	-	TongueUpRightMorph
Tongue_DownLeft_Morph	-	-	TongueDownLeftMorph
Tongue_DownRight_Morph	-	-	TongueDownRightMorph
Tongue_Roll	-	-	TongueRoll
			TongueBendDown
			TongueCurlUp
			TongueSquish
			TongueFlat
			TongueTwistLeft
			TongueTwistRight
			SoftPalateClose
			ThroatSwallow
			NeckFlexLeft
			NeckFlexRight
"""

_index_to_ft_type = [
	"sranipal",
	"arkit",
	"facs_reduced",
	"unified_expressions",
]

ft_definitions = {
	"unified_expressions": [],
	"arkit": [],
	"sranipal": [],
	"facs_reduced": [],
}

for line in ft_csv.splitlines():
	for index, entry in enumerate(line.split("\t")):
		if(entry and entry != "-"):
			ft_definitions[_index_to_ft_type[index]].append(entry)

