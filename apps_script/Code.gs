/**
 * Adds a custom menu to the Google Sheet UI
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Mail Automation')
    .addItem('Send Reports', 'sendPerformanceReports')
    .addToUi();
}

/**
 * Gets the correct suffix for a rank (1st, 2nd, 3rd, 4th, etc.)
 */
function getRankSuffix(rank) {
  const r = parseInt(rank, 10);
  if (isNaN(r)) return rank;
  const j = r % 10,
        k = r % 100;
  if (j == 1 && k != 11) return r + "st";
  if (j == 2 && k != 12) return r + "nd";
  if (j == 3 && k != 13) return r + "rd";
  return r + "th";
}

/**
 * Main function to generate charts and send emails
 */
function sendPerformanceReports() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const data = sheet.getDataRange().getValues();
  
  if (data.length < 3) {
    showAlert("Error", "Not enough data. Make sure you have the title row, header row, and at least one student row.");
    return;
  }
  
  // Show a toast message so the user knows it's running
  SpreadsheetApp.getActiveSpreadsheet().toast("Calculating averages and generating reports...", "Mail Automation", -1);
  
  // We use the sheet tab name as the test name (e.g., name your tab "Weekly Test-1")
  const testName = sheet.getName(); 
  
  // Connect to Google Drive Folder (checking for folder with or without a leading space, skipping trashed)
  let targetFolder = null;
  const folderNames = ["Student_Report_", " Student_Report_"];
  
  for (let i = 0; i < folderNames.length; i++) {
    const folders = DriveApp.getFoldersByName(folderNames[i]);
    while (folders.hasNext()) {
      const folder = folders.next();
      if (!folder.isTrashed()) {
        targetFolder = folder;
        break;
      }
    }
    if (targetFolder) break;
  }
  
  if (!targetFolder) {
    showAlert("Error", "Could not find an active Google Drive folder named 'Student_Report_' or ' Student_Report_'. Please create it and upload the PDFs.");
    return;
  }
  
  // Configuration
  const subjects = ['Physics', 'Chemistry', 'Maths'];
  const maxMarks = 100;
  const maxTotal = subjects.length * maxMarks;
  
  // Calculate class averages
  const classTotals = { Physics: 0, Chemistry: 0, Maths: 0 };
  let studentCount = 0;
  
  for (let i = 2; i < data.length; i++) { // Start from row 2 (index 2) to skip title and headers
    const row = data[i];
    if (row[0]) { // If Student Name exists (Column 0 is 'Name')
      classTotals.Physics += Number(row[5]) || 0; // 'P' is at index 5
      classTotals.Chemistry += Number(row[6]) || 0; // 'C' is at index 6
      classTotals.Maths += Number(row[4]) || 0; // 'M' is at index 4
      studentCount++;
    }
  }
  
  if (studentCount === 0) return;
  
  const classAverages = {
    Physics: (classTotals.Physics / studentCount).toFixed(1),
    Chemistry: (classTotals.Chemistry / studentCount).toFixed(1),
    Maths: (classTotals.Maths / studentCount).toFixed(1)
  };
  
  const totalClassAverage = (Number(classAverages.Physics) + Number(classAverages.Chemistry) + Number(classAverages.Maths)).toFixed(1);
  
  // Loop through each student and send email
  let emailsSent = 0;
  let skippedStudents = [];
  let failedStudents = [];
  let missingPdfs = [];
  
  for (let i = 2; i < data.length; i++) { // Start from row 2 (index 2)
    const row = data[i];
    const studentName = row[0]; // 'Name' is at index 0
    const rollNo = row[17]; // 'User Id' is at index 17
    
    if (!studentName) continue; // Skip empty rows
    
    const marks = {
      Physics: Number(row[5]) || 0, // 'P' is at index 5
      Chemistry: Number(row[6]) || 0, // 'C' is at index 6
      Maths: Number(row[4]) || 0 // 'M' is at index 4
    };
    
    const totalMarks = row[2]; // 'Marks' is at index 2
    const rank = row[1]; // 'Final Rank' is at index 1
    
    const emails = [];
    if (row[20]) emails.push(row[20].toString().trim()); // 'email_id_1' is at index 20
    if (row[21]) emails.push(row[21].toString().trim()); // 'email_id_2' is at index 21
    
    if (emails.length === 0) {
      Logger.log("Skipping " + studentName + " - No email found.");
      skippedStudents.push(studentName);
      continue;
    }
    
    const parentEmailsStr = emails.join(",");
    
    // Generate Chart
    const chartBlob = generateChart(studentName, marks, classAverages, subjects, maxMarks);
    
    // Setup HTML template
    const template = HtmlService.createTemplateFromFile('emailTemplate');
    template.studentName = studentName;
    template.rollNo = rollNo;
    template.testName = testName;
    template.rankSuffix = getRankSuffix(rank);
    template.marks = marks;
    template.classAverages = classAverages;
    template.totalMarks = totalMarks;
    template.totalClassAverage = totalClassAverage;
    template.maxTotal = maxTotal;
    
    const htmlBody = template.evaluate().getContent();
    
    // Fetch PDF from Drive (Case-Insensitive Match)
    let emailAttachments = [];
    let pdfName = "Student_Report_" + studentName.trim() + ".pdf";
    let file = findFileCaseInsensitive(targetFolder, pdfName);
    
    // Fallback: If full-name PDF is not found, try matching with just the First Name
    if (!file) {
      const firstName = studentName.trim().split(/\s+/)[0]; // Get first word
      pdfName = "Student_Report_" + firstName + ".pdf";
      file = findFileCaseInsensitive(targetFolder, pdfName);
    }
    
    if (file) {
      emailAttachments.push(file.getAs(MimeType.PDF));
    } else {
      missingPdfs.push(studentName);
      Logger.log("Missing PDF for: " + studentName + ". Email skipped.");
      continue; // Do not send email if PDF is missing
    }
    
    // Send email using the account running the script with Error Handling
    try {
      GmailApp.sendEmail(
        parentEmailsStr, 
        "Performance Report - " + studentName + " (" + testName + ")", 
        "Please enable HTML to view this email.", 
        {
          htmlBody: htmlBody,
          inlineImages: {
            chartImage: chartBlob
          },
          attachments: emailAttachments
        }
      );
      emailsSent++;
    } catch (e) {
      Logger.log("Failed to send email to " + studentName + " (" + parentEmailsStr + "). Error: " + e.message);
      failedStudents.push(studentName);
      SpreadsheetApp.getActiveSpreadsheet().toast("Failed to send to: " + studentName, "Warning");
    }
  }
  
  // Prepare final summary message
  let summaryMsg = "Successfully sent: " + emailsSent + " reports.\n";
  
  if (skippedStudents.length > 0) {
    summaryMsg += "\nSkipped (No Email Provided): " + skippedStudents.length + "\n- " + skippedStudents.join(", ") + "\n";
  }
  
  if (missingPdfs.length > 0) {
    summaryMsg += "\nFailed to Send (Report PDF was not in folder): " + missingPdfs.length + "\n- " + missingPdfs.join(", ") + "\n";
  }
  
  if (failedStudents.length > 0) {
    summaryMsg += "\nFailed to Send (Invalid Email/Error): " + failedStudents.length + "\n- " + failedStudents.join(", ") + "\n";
  }
  
  showAlert("Execution Summary", summaryMsg);
}

/**
 * Helper function to create a bar chart and return it as a Blob
 */
function generateChart(studentName, marks, classAverages, subjects, maxMarks) {
  const dataTable = Charts.newDataTable()
    .addColumn(Charts.ColumnType.STRING, 'Subject')
    .addColumn(Charts.ColumnType.NUMBER, studentName + "'s Marks")
    .addColumn(Charts.ColumnType.NUMBER, 'Class Average');
    
  for (let i = 0; i < subjects.length; i++) {
    const sub = subjects[i];
    dataTable.addRow([sub, marks[sub], Number(classAverages[sub])]);
  }
  
  const chart = Charts.newColumnChart()
    .setDataTable(dataTable)
    .setTitle('Your Child vs Class Average (out of ' + maxMarks + ')')
    .setDimensions(800, 400)
    .setRange(0, maxMarks)
    .setColors(['#0073E6', '#C0C0C0']) // Bright blue & light gray
    .setOption('legend', {position: 'bottom'})
    .setOption('vAxis', {gridlines: {color: '#AAAAAA'}})
    .build();
    
  return chart.getAs('image/png');
}

/**
 * Helper function to find a file in a folder case-insensitively
 */
function findFileCaseInsensitive(folder, targetName) {
  const files = folder.getFiles();
  const targetLower = targetName.toLowerCase().trim();
  while (files.hasNext()) {
    const file = files.next();
    if (file.getName().toLowerCase().trim() === targetLower) {
      return file;
    }
  }
  return null;
}

/**
 * Helper function to show UI alert, falling back to logger if run from the editor console
 */
function showAlert(title, message) {
  try {
    const ui = SpreadsheetApp.getUi();
    ui.alert(title, message, ui.ButtonSet.OK);
  } catch (e) {
    Logger.log("[" + title + "] " + message);
  }
}
