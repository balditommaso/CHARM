import json
import numpy as np


def find_col_out(col_sel, chl_cnt, reverse, num_channel):
    """Recursive function to find available PLIO ports (OUT)."""
    if col_sel > 44 or col_sel < 6:
        return 0, 0

    cnt_pos = col_sel - 6
    chl_num = chl_cnt[cnt_pos]

    if chl_num < num_channel:
        return col_sel, chl_num
    else:
        col_sel = col_sel + reverse
        return find_col_out(col_sel, chl_cnt, reverse, num_channel)


def find_col_in(col_sel, chl_cnt, chl_lhs_flag, reverse, op):
    """Recursive function to find available PLIO ports (IN).
    op: 0 -> LHS, 1 -> RHS
    """
    if col_sel > 44 or col_sel < 6:
        return 0, 0

    cnt_pos = col_sel - 6
    chl_num = chl_cnt[cnt_pos]
    lhs_flag = chl_lhs_flag[cnt_pos]

    if lhs_flag == 0:
        num_channel = 2 if op == 0 else 4
    else:
        num_channel = 2

    if chl_num < num_channel:
        return col_sel, chl_num
    else:
        col_sel = col_sel + reverse
        return find_col_in(col_sel, chl_cnt, chl_lhs_flag, reverse, op)


def plio_placement(HW_Config):
    dictionary = {"NodeConstraints": {}}
    layer = HW_Config.shape[0]

    chl_cnt_in = np.zeros(39)
    chl_lhs_flag = np.zeros(39)
    chl_cnt_out = np.zeros(39)

    for acc in range(layer):
        A = HW_Config[acc][0]
        B = HW_Config[acc][1]
        C = HW_Config[acc][2]
        A_BRO = HW_Config[acc][3]
        C_BRO = HW_Config[acc][4]
        PACK_IN = HW_Config[acc][5]
        PACK_OUT = HW_Config[acc][6]
        pos_col = HW_Config[acc][7]
        pos_row = HW_Config[acc][8]
        height = HW_Config[acc][9]

        c_a_bro = C // A_BRO
        num_chl_out = 2

        # -------------------------------
        # LHS PLIO Placement
        # -------------------------------
        for i in range(A):
            for j in range(C // A_BRO):
                for k in range(B // PACK_IN):
                    port_num = k + j * (B // PACK_IN) + i * (C // A_BRO) * (B // PACK_IN)
                    port_name = f"LHS_in{port_num}_L{acc}"

                    dictionary["NodeConstraints"][port_name] = {
                        "shim": {"column": {}, "channel": {}}
                    }

                    if c_a_bro % 2 == 0 and height % 2 == 0:
                        if (j // (c_a_bro / 2)) == 1:
                            if pos_row % 2 == 0:
                                reverse, offset = -1, 1
                            else:
                                reverse, offset = 1, 0
                        else:
                            if pos_row % 2 == 0:
                                reverse, offset = 1, 0
                            else:
                                reverse, offset = -1, 1

                        cur_col = (
                            pos_col
                            + reverse * k * PACK_IN
                            + (j % (c_a_bro / 2)) * B
                            + offset * (B - 1)
                            + i * B * (C // height)
                        )
                    else:
                        reverse = 1
                        cur_col = pos_col + k * PACK_IN + j * B + i * B * (C // height)

                    col_sel = int(np.clip(cur_col, 6, 44))
                    col_sel_new, chl_num = find_col_in(
                        col_sel, chl_cnt_in, chl_lhs_flag, reverse, 0
                    )

                    if col_sel_new == 0:
                        reverse = -reverse
                        col_sel_new, chl_num = find_col_in(
                            col_sel, chl_cnt_in, chl_lhs_flag, reverse, 0
                        )
                        if col_sel_new == 0:
                            print("\n\n\nLHS PLIO failed to place\n\n\n")
                            break

                    chl_sel = ((chl_num + 1) * 2) % 8

                    dictionary["NodeConstraints"][port_name]["shim"]["column"] = int(
                        col_sel_new
                    )
                    dictionary["NodeConstraints"][port_name]["shim"]["channel"] = int(
                        chl_sel
                    )

                    chl_cnt_in[col_sel_new - 6] += 1
                    chl_lhs_flag[col_sel_new - 6] = 1

        # -------------------------------
        # RHS PLIO Placement
        # -------------------------------
        for j in range(C):
            for i in range(A // C_BRO):
                for k in range(B // PACK_IN):
                    port_num = k + i * (B // PACK_IN) + j * (A // C_BRO) * (B // PACK_IN)
                    port_name = f"RHS_in{port_num}_L{acc}"

                    dictionary["NodeConstraints"][port_name] = {
                        "shim": {"column": {}, "channel": {}}
                    }

                    if c_a_bro % 2 == 0 and height % 2 == 0:
                        if pos_row % 2 == 0:
                            if j // (C // 2) == 0:
                                reverse, offset = 1, 0
                            else:
                                reverse, offset = -1, 1
                        else:
                            if j // (C // 2) == 0:
                                reverse, offset = -1, 1
                            else:
                                reverse, offset = 1, 0
                    else:
                        if (j + pos_row) % 2 == 0:
                            reverse, offset = 1, 0
                        else:
                            reverse, offset = -1, 1

                    cur_col = (
                        pos_col
                        + reverse * k * PACK_IN
                        + i * B * (C // height) * C_BRO
                        + offset * (B * (C // height) * C_BRO - 1)
                    )

                    col_sel = int(np.clip(cur_col, 6, 44))
                    col_sel_new, chl_num = find_col_in(
                        col_sel, chl_cnt_in, chl_lhs_flag, reverse, 1
                    )

                    if col_sel_new == 0:
                        reverse = -reverse
                        col_sel_new, chl_num = find_col_in(
                            col_sel, chl_cnt_in, chl_lhs_flag, reverse, 1
                        )
                        if col_sel_new == 0:
                            print("\n\n\nRHS PLIO failed to place\n\n\n")
                            break

                    chl_sel = ((chl_num + 1) * 2) % 8

                    dictionary["NodeConstraints"][port_name]["shim"]["column"] = int(
                        col_sel_new
                    )
                    dictionary["NodeConstraints"][port_name]["shim"]["channel"] = int(
                        chl_sel
                    )

                    chl_cnt_in[col_sel_new - 6] += 1

        # -------------------------------
        # OUT PLIO Placement
        # -------------------------------
        if height % PACK_OUT == 0:
            for i in range(A):
                for j in range(C // PACK_OUT):
                    port_num = j + i * (C // PACK_OUT)
                    port_name = f"out{port_num}_L{acc}"

                    dictionary["NodeConstraints"][port_name] = {
                        "shim": {"column": {}, "channel": {}}
                    }

                    if c_a_bro % 2 == 0 and height % 2 == 0:
                        if (C // PACK_OUT) == 1:
                            if pos_row % 2 == 0:
                                reverse, offset = 1, 1
                            else:
                                reverse, offset = -1, 0
                        elif j // ((C // PACK_OUT) / 2) == 0:
                            if pos_row % 2 == 0:
                                reverse, offset = 1, 1
                            else:
                                reverse, offset = -1, 0
                        else:
                            if pos_row % 2 == 0:
                                reverse, offset = -1, 0
                            else:
                                reverse, offset = 1, 1

                        cur_col = pos_col + offset * (B - 1) + i * B * (C // height)
                    else:
                        reverse = 1
                        cur_col = pos_col + i * B * (C // height)

                    col_sel = int(np.clip(cur_col, 6, 44))
                    col_sel_new, chl_num = find_col_out(
                        col_sel, chl_cnt_out, reverse, num_chl_out
                    )

                    if col_sel_new == 0:
                        reverse = -reverse
                        col_sel_new, chl_num = find_col_out(
                            col_sel, chl_cnt_out, reverse, num_chl_out
                        )
                        if col_sel_new == 0:
                            print("\n\n\nOUT PLIO failed to place\n\n\n")
                            break

                    chl_sel = ((chl_num + 1) * 2) % 8

                    dictionary["NodeConstraints"][port_name]["shim"]["column"] = int(
                        col_sel_new
                    )
                    dictionary["NodeConstraints"][port_name]["shim"]["channel"] = int(
                        chl_sel
                    )

                    chl_cnt_out[col_sel_new - 6] += 1

    return json.dumps(dictionary, indent=4)
