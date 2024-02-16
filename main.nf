process callPython {
    debug true
    container 'sagebionetworks/genie:latest'

    script:
    """
    python3 /home/ec2-user/test_bash/call_bash_from_python.py
    """

    // Declare output file directly
    output:
    file "output.txt"
   
}

workflow {
    callPython()
}
