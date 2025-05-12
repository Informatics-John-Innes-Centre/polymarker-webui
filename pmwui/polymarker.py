import os
import subprocess

from pmwui.mail import send_massage


def get_reference_cmd_data(db, ref_id):
    cursor = db.cursor()
    cursor.execute("SELECT path, genome_count, arm_selection FROM reference WHERE name = %s", (ref_id,))
    reference = cursor.fetchone()
    return reference


def get_query_cmd_data(db, uid):
    cursor = db.cursor()
    cursor.execute("SELECT reference, email FROM query WHERE uid = %s", (uid,))
    reference = cursor.fetchone()
    return reference



def update_query_status(db, uid, status):
    cursor = db.cursor()
    cursor.execute("UPDATE query SET status=? WHERE uid=?", (status, uid))
    db.commit()
    cursor.close()


def post_process_masks(src, des):
    src_file = open(src, 'r')
    des_file = open(des, 'w')

    mask = False
    skip = False

    for line in src_file:
        if skip and line.startswith(">"):
            skip = False

        if mask and line.startswith(">"):
            skip = True
            mask = False
            continue

        if line.startswith(">MASK"):
            mask = True

        if skip:
            continue

        des_file.write(line)

    des_file.close()
    src_file.close()


def run_pm(db, input_dir, output_dir, uid, mail_app):
    query_ref = get_query_cmd_data(db, uid)

    # log.info("$$$$$$$$$$$$$$$$$$$$")
    # log.info(query_ref)
    print("rpm:", query_ref)
    # log.info("$$$$$$$$$$$$$$$$$$$$")

    filename = f"{uid}.csv"
    ref_data = get_reference_cmd_data(db, query_ref[0])

    # log.info(ref_data)
    print("REFDATA:", ref_data)

    ref_path = ref_data[0]
    ref_genome_count = ref_data[1]
    ref_arm_selection = ref_data[2]

    cmd = f"ulimit -v 6000000; polymarker.rb -m {os.path.join(input_dir, filename)} -o {output_dir}/{uid}_out -c {ref_path} -g {ref_genome_count} -a {ref_arm_selection} -A blast"
    # log.info(command)
    result = subprocess.run(cmd, shell=True)

    # log.info(result)
    print(result)

    update_query_status(db, uid, str(result))

    # log.info("_____________")
    # log.info(app.static_folder)
    # log.info("_____________")

    # log.info(os.listdir(app.static_folder))

    os.rename(f"{output_dir}/{uid}_out/exons_genes_and_contigs.fa",
              f"{output_dir}/{uid}_out/exons_genes_and_contigs.fa.og")

    post_process_masks(f"{output_dir}/{uid}_out/exons_genes_and_contigs.fa.og",
                       f"{output_dir}/{uid}_out/exons_genes_and_contigs.fa")



    query_ref = get_query_cmd_data(db, uid)

    if query_ref[1] != "":
        with open(f"{output_dir}/{uid}_out/status.txt", 'r') as f:
            lines = f.read().splitlines()
            status = lines[-1]
            with mail_app.app_context():
                send_massage(mail_app.mail, query_ref[1], uid, status)



    # todo: do stuff now we are done?
    # rest_done(uid)

