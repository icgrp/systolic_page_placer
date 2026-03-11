//*****************************************************************************************************************
// print the arch types and their max fanin
auto& device_ctx = g_vpr_ctx.device();
auto& place_ctx = g_vpr_ctx.mutable_placement();
place_ctx.compressed_block_grids = create_compressed_block_grids();

printf("printing systolic_arch_types\n");
FILE *fp = NULL;
fp = fopen("systolic_arch_info","w");
if(fp != NULL)
{
    fprintf(fp,"type\tfanin\n");
    for(auto physical_tile_type : device_ctx.physical_tile_types)
    {
        fprintf(fp,"%s\t%d\n",physical_tile_type.name.c_str(),physical_tile_type.num_input_pins + physical_tile_type.num_clock_pins);
    }
}
fclose(fp);
//*****************************************************************************************************************
// print the device grid
printf("printing systolic_grid_info\n");
fp = fopen("systolic_grid_info","w");
if(fp != NULL)
{
    fprintf(fp,"%lu by %lu\n",device_ctx.grid.width(),device_ctx.grid.height());
    fprintf(fp,"type\tcx\tcy\tx\ty\n");
    for(auto physical_tile_type : device_ctx.physical_tile_types)
    {
        const auto& compressed_block_grid = g_vpr_ctx.placement().compressed_block_grids[physical_tile_type.index];
        int cx_size = compressed_block_grid.compressed_to_grid_x[0].size();
        int cy_size = compressed_block_grid.compressed_to_grid_y[0].size();

        if(physical_tile_type.name != "io")
        {
            for(int cx = 0; cx < cx_size; cx++)
            {
                for(int cy = 0; cy < cy_size; cy++)
                {
                    int x = compressed_block_grid.compressed_to_grid_x[0][cx];
                    int y = compressed_block_grid.compressed_to_grid_y[0][cy];
                    fprintf(fp,"%s\t%d\t%d\t%d\t%d\n",physical_tile_type.name.c_str(),cx,cy,x,y);
                }
            }
        }
    }
}
vtr::release_memory(place_ctx.compressed_block_grids);
fclose(fp);
//*****************************************************************************************************************
// print the netlist info
fp = fopen("systolic_netlist_info","w");
if(fp != NULL)
{
    printf("printing systolic_netlist_info\n");
    fprintf(fp,"Netlist_File %s Netlist_ID: %s\n",filename_opts.NetFile.c_str(),cluster_ctx.clb_nlist.netlist_id().c_str());
    fprintf(fp,"blk_name blk_type blk_id, connected_blk_name, connected_blk_name, ...\n");
    for(auto blk_id : cluster_ctx.clb_nlist.blocks())
    {
        fprintf(fp,"%s ",cluster_ctx.clb_nlist.block_name(blk_id).c_str());
        fprintf(fp,"%s ",cluster_ctx.clb_nlist.block_type(blk_id)->name.c_str());
        fprintf(fp,"%d",blk_id);
        for(auto& pin_id : cluster_ctx.clb_nlist.block_input_pins(blk_id))
        {
            auto net_id = cluster_ctx.clb_nlist.pin_net(pin_id);
            auto net_driver = cluster_ctx.clb_nlist.net_driver(net_id);
            auto connected_blk_id = cluster_ctx.clb_nlist.pin_block(net_driver);
            if(connected_blk_id != blk_id)
            {
                fprintf(fp,",%s",cluster_ctx.clb_nlist.block_name(connected_blk_id).c_str());
            }
        }
        for(auto& pin_id : cluster_ctx.clb_nlist.block_output_pins(blk_id))
        {
            auto net_id = cluster_ctx.clb_nlist.pin_net(pin_id);
            for(auto& sink_pin : cluster_ctx.clb_nlist.net_sinks(net_id))
            {
                auto connected_blk_id = cluster_ctx.clb_nlist.pin_block(sink_pin);
                if(connected_blk_id != blk_id)
                {
                    fprintf(fp,",%s",cluster_ctx.clb_nlist.block_name(connected_blk_id).c_str());
                }
            }
        }
        for(auto& pin_id : cluster_ctx.clb_nlist.block_clock_pins(blk_id))
        {
            auto net_id = cluster_ctx.clb_nlist.pin_net(pin_id);
            auto net_driver = cluster_ctx.clb_nlist.net_driver(net_id);
            auto connected_blk_id = cluster_ctx.clb_nlist.pin_block(net_driver);
            if(connected_blk_id != blk_id)
            {
                fprintf(fp,",%s",cluster_ctx.clb_nlist.block_name(connected_blk_id).c_str());
            }
        }
        fprintf(fp,"\n");
    }
    fclose(fp);
}
//*****************************************************************************************************************