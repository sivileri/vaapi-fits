pushd ~/repos/vaapi-fits/assets/DXVAContent/

#H264
ffmpeg -i Dancing_1920x1088_6mbps_25fps_High_at_L4.1_Cavlc.mp4 -vcodec copy Dancing_1920x1088_6mbps_25fps_High_at_L4.1_Cavlc.h264
ffmpeg -i Dancing_1920x1088_9mbps_25fps_Main_at_L4.1_Cabac_NoFrext.mp4 -vcodec copy Dancing_1920x1088_9mbps_25fps_Main_at_L4.1_Cabac_NoFrext.h264
ffmpeg -i Dancing_1920x1088i_6mbps_25fps_High_at_L4.1_Cabac_Frext.mp4 -vcodec copy Dancing_1920x1088i_6mbps_25fps_High_at_L4.1_Cabac_Frext.h264
ffmpeg -i Dancing_1920x1088i_8mbps_25fps_Main_at_L4.1_Cabac_Frext_Frm.mp4 -vcodec copy Dancing_1920x1088i_8mbps_25fps_Main_at_L4.1_Cabac_Frext_Frm.h264
ffmpeg -i Dancing_1920x1088i_9mbps_25fps_Main_at_L4.1_Cabac_PureMbaff.mp4 -vcodec copy Dancing_1920x1088i_9mbps_25fps_Main_at_L4.1_Cabac_PureMbaff.h264
ffmpeg -i Dancing_1920x1088p_9mbps_25fps_High_at_L4.1_Cabac_Frext.mp4 -vcodec copy Dancing_1920x1088p_9mbps_25fps_High_at_L4.1_Cabac_Frext.h264
ffmpeg -i Lanczos_Mobileportrait_720x1280p_9mbps_25fps_Main_at_L3.1_Cabac.mp4 -vcodec copy Lanczos_Mobileportrait_720x1280p_9mbps_25fps_Main_at_L3.1_Cabac.h264
ffmpeg -i Singing_320x240p_62kbps_24fps_Baseline_at_L3.0_TextureSkinTones.mp4 -vcodec copy Singing_320x240p_62kbps_24fps_Baseline_at_L3.0_TextureSkinTones.h264
ffmpeg -i Soccer_1280x720p_3mbps_25fps_High_at_L4.1_Cabac_frext_slice.mp4 -vcodec copy Soccer_1280x720p_3mbps_25fps_High_at_L4.1_Cabac_frext_slice.h264
ffmpeg -i Soccer_544x480i_2mbps_29.97fps_Main_at_L3.0_Cabac.mp4 -vcodec copy Soccer_544x480i_2mbps_29.97fps_Main_at_L3.0_Cabac.h264
ffmpeg -i Tallship_1920x1088_10mbps_25fps_High_at_L4.1_Cabac_Mbaff.mp4 -vcodec copy Tallship_1920x1088_10mbps_25fps_High_at_L4.1_Cabac_Mbaff.h264
ffmpeg -i Tallship_1920x1088_10mbps_25fps_High_at_L4.1_Cabac_Prog.mp4 -vcodec copy Tallship_1920x1088_10mbps_25fps_High_at_L4.1_Cabac_Prog.h264
ffmpeg -i Tallship_1920x1088i_field_14mbps_25fps_High_at_L4.1_Cabac_Slice.mp4 -vcodec copy Tallship_1920x1088i_field_14mbps_25fps_High_at_L4.1_Cabac_Slice.h264
ffmpeg -i Tallship_720x480p_5mbps_24fps_Main_at_L3.2_CABAC_DifficultEdge.mp4 -vcodec copy Tallship_720x480p_5mbps_24fps_Main_at_L3.2_CABAC_DifficultEdge.h264
ffmpeg -i tearsofsteel_4k_60s_24fps.12000kbps.3840x2160.h264-8b.2ch.128kbps.aac.mp4 -vcodec copy tearsofsteel_4k_60s_24fps.12000kbps.3840x2160.h264-8b.2ch.128kbps.aac.h264

# HEVC
ffmpeg -i HEVC_3840x2160_64tiles_sao_no_cross_tile.mp4 -vcodec copy HEVC_3840x2160_64tiles_sao_no_cross_tile.h265
ffmpeg -i HEVC_4096x2160_64tiles_sao_cross_tile.mp4 -vcodec copy HEVC_4096x2160_64tiles_sao_cross_tile.h265
ffmpeg -i HEVC_4096x2160_64tiles_sao_no_cross_tile.mp4 -vcodec copy HEVC_4096x2160_64tiles_sao_no_cross_tile.h265
ffmpeg -i MSHDRef_Difficult_Edge_02_720x480i30f_intra_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_02_720x480i30f_intra_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_02_720x480i30f_lowdelay_P_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_02_720x480i30f_lowdelay_P_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_02_720x480i30f_lowdelay_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_02_720x480i30f_lowdelay_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_02_720x480p24f_lowdelay_P_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_02_720x480p24f_lowdelay_P_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_02_720x480p30f_1047kbps_randomaccess_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_02_720x480p30f_1047kbps_randomaccess_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_02_720x480p30f_1739kbps_randomaccess_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_02_720x480p30f_1739kbps_randomaccess_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_02_720x480p30f_560kbps_randomaccess_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_02_720x480p30f_560kbps_randomaccess_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_02_720x480p30f_intra_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_02_720x480p30f_intra_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_02_720x480p30f_lowdelay_P_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_02_720x480p30f_lowdelay_P_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_02_720x480p30f_lowdelay_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_02_720x480p30f_lowdelay_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_06_720x576i25f_intra_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_06_720x576i25f_intra_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_06_720x576i25f_lowdelay_P_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_06_720x576i25f_lowdelay_P_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_06_720x576i25f_randomaccess_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_06_720x576i25f_randomaccess_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_06_720x576p25f_intra_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_06_720x576p25f_intra_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_06_720x576p25f_lowdelay_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_06_720x576p25f_lowdelay_main.h265
ffmpeg -i MSHDRef_Difficult_Edge_06_720x576p25f_randomaccess_main.mp4 -vcodec copy MSHDRef_Difficult_Edge_06_720x576p25f_randomaccess_main.h265
ffmpeg -i MSHDRef_Motion_DifDirect_01_1280x720p24f_2983kbps_randomaccess_main.mp4 -vcodec copy MSHDRef_Motion_DifDirect_01_1280x720p24f_2983kbps_randomaccess_main.h265
ffmpeg -i MSHDRef_Motion_DifDirect_01_1280x720p24f_intra_main.mp4 -vcodec copy MSHDRef_Motion_DifDirect_01_1280x720p24f_intra_main.h265
ffmpeg -i MSHDRef_Motion_DifDirect_01_1280x720p24f_lowdelay_P_main.mp4 -vcodec copy MSHDRef_Motion_DifDirect_01_1280x720p24f_lowdelay_P_main.h265
ffmpeg -i MSHDRef_Motion_FastCam_Action_03_1920x1080i30f_intra_main.mp4 -vcodec copy MSHDRef_Motion_FastCam_Action_03_1920x1080i30f_intra_main.h265
ffmpeg -i MSHDRef_Motion_FastCam_Action_03_1920x1080i30f_lowdelay_P_main.mp4 -vcodec copy MSHDRef_Motion_FastCam_Action_03_1920x1080i30f_lowdelay_P_main.h265
ffmpeg -i MSHDRef_Motion_FastCam_Action_03_1920x1080i30f_lowdelay_main.mp4 -vcodec copy MSHDRef_Motion_FastCam_Action_03_1920x1080i30f_lowdelay_main.h265
ffmpeg -i MSHDRef_Motion_FastCam_Action_03_1920x1080p24f_3834kbps_randomaccess_main.mp4 -vcodec copy MSHDRef_Motion_FastCam_Action_03_1920x1080p24f_3834kbps_randomaccess_main.h265
ffmpeg -i MSHDRef_Motion_FastCam_Action_03_1920x1080p24f_intra_main.mp4 -vcodec copy MSHDRef_Motion_FastCam_Action_03_1920x1080p24f_intra_main.h265
ffmpeg -i MSHDRef_Motion_FastCam_Action_03_1920x1080p24f_lowdelay_P_main.mp4 -vcodec copy MSHDRef_Motion_FastCam_Action_03_1920x1080p24f_lowdelay_P_main.h265
ffmpeg -i MSHDRef_Motion_FastCam_Action_03_1920x1080p24f_lowlevel_main.mp4 -vcodec copy MSHDRef_Motion_FastCam_Action_03_1920x1080p24f_lowlevel_main.h265
ffmpeg -i MSHDRef_Texture_High_01_320x240p30f_lowdelay_main.mp4 -vcodec copy MSHDRef_Texture_High_01_320x240p30f_lowdelay_main.h265
ffmpeg -i MSHDRef_Texture_High_01_320x240p30f_randomaccess_main.mp4 -vcodec copy MSHDRef_Texture_High_01_320x240p30f_randomaccess_main.h265
ffmpeg -i MSHDRef_Texture_SkinTones_05_352x288p15f_intra_main.mp4 -vcodec copy MSHDRef_Texture_SkinTones_05_352x288p15f_intra_main.h265
ffmpeg -i MSHDRef_Texture_SkinTones_05_352x288p15f_lowdelay_P_main.mp4 -vcodec copy MSHDRef_Texture_SkinTones_05_352x288p15f_lowdelay_P_main.h265
ffmpeg -i MSHDRef_Texture_SkinTones_05_352x288p15f_lowdelay_main.mp4 -vcodec copy MSHDRef_Texture_SkinTones_05_352x288p15f_lowdelay_main.h265
ffmpeg -i MSHDRef_Texture_SkinTones_05_352x288p15f_randomaccess_main.mp4 -vcodec copy MSHDRef_Texture_SkinTones_05_352x288p15f_randomaccess_main.h265
ffmpeg -i MSHDRef_Texture_SkinTones_05_352x288p25f_intra_main.mp4 -vcodec copy MSHDRef_Texture_SkinTones_05_352x288p25f_intra_main.h265
ffmpeg -i MSHDRef_Texture_SkinTones_05_352x288p25f_lowdelay_P_main.mp4 -vcodec copy MSHDRef_Texture_SkinTones_05_352x288p25f_lowdelay_P_main.h265
ffmpeg -i MSHDRef_Texture_SkinTones_05_352x288p25f_lowdelay_main.mp4 -vcodec copy MSHDRef_Texture_SkinTones_05_352x288p25f_lowdelay_main.h265
ffmpeg -i MSHDRef_Texture_SkinTones_08_320x240p24f_lowdelay_P_main.mp4 -vcodec copy MSHDRef_Texture_SkinTones_08_320x240p24f_lowdelay_P_main.h265
ffmpeg -i MSHDRef_Texture_SkinTones_08_320x240p24f_lowlevel_main.mp4 -vcodec copy MSHDRef_Texture_SkinTones_08_320x240p24f_lowlevel_main.h265
ffmpeg -i MSHDRef_Texture_SkinTones_08_320x240p24f_randomaccess_main.mp4 -vcodec copy MSHDRef_Texture_SkinTones_08_320x240p24f_randomaccess_main.h265
ffmpeg -i tearsofsteel_4k_60s_24fps.12000kbps.3840x2160.h265-8b.2ch.128kbps.aac.mp4 -vcodec copy tearsofsteel_4k_60s_24fps.12000kbps.3840x2160.h265-8b.2ch.128kbps.aac.h265
ffmpeg -i 4K_10bit.mp4 -vcodec copy 4K_10bit.h265
ffmpeg -i tearsofsteel_4k_60s_24fps.12000kbps.3840x2160.h265-10b.2ch.128kbps.aac.mp4 -vcodec copy tearsofsteel_4k_60s_24fps.12000kbps.3840x2160.h265-10b.2ch.128kbps.aac.h265

# Delete them after extracting the assets
rm -f Dancing_1920x1088_6mbps_25fps_High_at_L4.1_Cavlc.mp4
rm -f Dancing_1920x1088_9mbps_25fps_Main_at_L4.1_Cabac_NoFrext.mp4
rm -f Dancing_1920x1088i_6mbps_25fps_High_at_L4.1_Cabac_Frext.mp4
rm -f Dancing_1920x1088i_8mbps_25fps_Main_at_L4.1_Cabac_Frext_Frm.mp4
rm -f Dancing_1920x1088i_9mbps_25fps_Main_at_L4.1_Cabac_PureMbaff.mp4
rm -f Dancing_1920x1088p_9mbps_25fps_High_at_L4.1_Cabac_Frext.mp4
rm -f Lanczos_Mobileportrait_720x1280p_9mbps_25fps_Main_at_L3.1_Cabac.mp4
rm -f Singing_320x240p_62kbps_24fps_Baseline_at_L3.0_TextureSkinTones.mp4
rm -f Soccer_1280x720p_3mbps_25fps_High_at_L4.1_Cabac_frext_slice.mp4
rm -f Soccer_544x480i_2mbps_29.97fps_Main_at_L3.0_Cabac.mp4
rm -f Tallship_1920x1088_10mbps_25fps_High_at_L4.1_Cabac_Mbaff.mp4
rm -f Tallship_1920x1088_10mbps_25fps_High_at_L4.1_Cabac_Prog.mp4
rm -f Tallship_1920x1088i_field_14mbps_25fps_High_at_L4.1_Cabac_Slice.mp4
rm -f Tallship_720x480p_5mbps_24fps_Main_at_L3.2_CABAC_DifficultEdge.mp4
rm -f tearsofsteel_4k_60s_24fps.12000kbps.3840x2160.h264-8b.2ch.128kbps.aac.mp4
rm -f HEVC_3840x2160_64tiles_sao_no_cross_tile.mp4
rm -f HEVC_4096x2160_64tiles_sao_cross_tile.mp4
rm -f HEVC_4096x2160_64tiles_sao_no_cross_tile.mp4
rm -f MSHDRef_Difficult_Edge_02_720x480i30f_intra_main.mp4
rm -f MSHDRef_Difficult_Edge_02_720x480i30f_lowdelay_P_main.mp4
rm -f MSHDRef_Difficult_Edge_02_720x480i30f_lowdelay_main.mp4
rm -f MSHDRef_Difficult_Edge_02_720x480p24f_lowdelay_P_main.mp4
rm -f MSHDRef_Difficult_Edge_02_720x480p30f_1047kbps_randomaccess_main.mp4
rm -f MSHDRef_Difficult_Edge_02_720x480p30f_1739kbps_randomaccess_main.mp4
rm -f MSHDRef_Difficult_Edge_02_720x480p30f_560kbps_randomaccess_main.mp4
rm -f MSHDRef_Difficult_Edge_02_720x480p30f_intra_main.mp4
rm -f MSHDRef_Difficult_Edge_02_720x480p30f_lowdelay_P_main.mp4
rm -f MSHDRef_Difficult_Edge_02_720x480p30f_lowdelay_main.mp4
rm -f MSHDRef_Difficult_Edge_06_720x576i25f_intra_main.mp4
rm -f MSHDRef_Difficult_Edge_06_720x576i25f_lowdelay_P_main.mp4
rm -f MSHDRef_Difficult_Edge_06_720x576i25f_randomaccess_main.mp4
rm -f MSHDRef_Difficult_Edge_06_720x576p25f_intra_main.mp4
rm -f MSHDRef_Difficult_Edge_06_720x576p25f_lowdelay_main.mp4
rm -f MSHDRef_Difficult_Edge_06_720x576p25f_randomaccess_main.mp4
rm -f MSHDRef_Motion_DifDirect_01_1280x720p24f_2983kbps_randomaccess_main.mp4
rm -f MSHDRef_Motion_DifDirect_01_1280x720p24f_intra_main.mp4
rm -f MSHDRef_Motion_DifDirect_01_1280x720p24f_lowdelay_P_main.mp4
rm -f MSHDRef_Motion_FastCam_Action_03_1920x1080i30f_intra_main.mp4
rm -f MSHDRef_Motion_FastCam_Action_03_1920x1080i30f_lowdelay_P_main.mp4
rm -f MSHDRef_Motion_FastCam_Action_03_1920x1080i30f_lowdelay_main.mp4
rm -f MSHDRef_Motion_FastCam_Action_03_1920x1080p24f_3834kbps_randomaccess_main.mp4
rm -f MSHDRef_Motion_FastCam_Action_03_1920x1080p24f_intra_main.mp4
rm -f MSHDRef_Motion_FastCam_Action_03_1920x1080p24f_lowdelay_P_main.mp4
rm -f MSHDRef_Motion_FastCam_Action_03_1920x1080p24f_lowlevel_main.mp4
rm -f MSHDRef_Texture_High_01_320x240p30f_lowdelay_main.mp4
rm -f MSHDRef_Texture_High_01_320x240p30f_randomaccess_main.mp4
rm -f MSHDRef_Texture_SkinTones_05_352x288p15f_intra_main.mp4
rm -f MSHDRef_Texture_SkinTones_05_352x288p15f_lowdelay_P_main.mp4
rm -f MSHDRef_Texture_SkinTones_05_352x288p15f_lowdelay_main.mp4
rm -f MSHDRef_Texture_SkinTones_05_352x288p15f_randomaccess_main.mp4
rm -f MSHDRef_Texture_SkinTones_05_352x288p25f_intra_main.mp4
rm -f MSHDRef_Texture_SkinTones_05_352x288p25f_lowdelay_P_main.mp4
rm -f MSHDRef_Texture_SkinTones_05_352x288p25f_lowdelay_main.mp4
rm -f MSHDRef_Texture_SkinTones_08_320x240p24f_lowdelay_P_main.mp4
rm -f MSHDRef_Texture_SkinTones_08_320x240p24f_lowlevel_main.mp4
rm -f MSHDRef_Texture_SkinTones_08_320x240p24f_randomaccess_main.mp4
rm -f tearsofsteel_4k_60s_24fps.12000kbps.3840x2160.h265-8b.2ch.128kbps.aac.mp4
rm -f 4K_10bit.mp4
rm -f tearsofsteel_4k_60s_24fps.12000kbps.3840x2160.h265-10b.2ch.128kbps.aac.mp4

popd # ~/repos/vaapi-fits/assets/DXVAContent/
