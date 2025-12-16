
# paths to be exported
export XILINX_XRT=/opt/xilinx/xrt
export PLATFORM=/home/tommaso/tools/Xilinx/2025.1/Vitis/base_platforms/xilinx_vck190_base_202510_1
export SYSROOT=/home/tommaso/tools/petalinux/2025.1/sysroots/cortexa72-cortexa53-xilinx-linux
export EDGE_COMMON_SW=/media/tommaso/_data/images/versal-common-v2025.1
# # export XILINXD_LICENSE_FILE=/home/t.baldi/projects/AIE_xilinx.lic
export PLATFORM=/home/tommaso/tools/Xilinx/2025.1/Vitis/base_platforms/xilinx_vck190_base_202510_1/xilinx_vck190_base_202510_1.xpfm
# source
source /home/tommaso/tools/Xilinx/2025.1/Vitis/settings64.sh
source $XILINX_XRT/setup.sh
unset LD_LIBRARY_PATH
source /home/tommaso/tools/petalinux/2025.1/environment-setup-cortexa72-cortexa53-amd-linux
