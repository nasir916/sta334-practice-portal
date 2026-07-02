/**
 * Google Apps Script - Automated Student PDF Uploader
 * 
 * Instructions:
 * 1. Open Google Drive (under the account where you want files saved).
 * 2. Go to https://script.google.com/ and create a new project.
 * 3. Delete any default code and paste this code.
 * 4. Click the Save icon.
 * 5. Click "Deploy" -> "New deployment".
 * 6. Select type "Web app".
 * 7. Set:
 *    - Description: Student PDF Uploader
 *    - Execute as: "Me" (your lecturer email)
 *    - Who has access: "Anyone" (crucial for student web apps to upload)
 * 8. Click "Deploy". Authorize permissions if prompted.
 * 9. Copy the "Web app URL" (it ends with /exec).
 * 10. Paste this URL into the Admin Settings inside the R Practice App to enable automatic uploads!
 */

function doPost(e) {
  try {
    // Parse the incoming JSON payload
    var data = JSON.parse(e.postData.contents);
    
    // Decode base64 file data
    var fileContent = Utilities.base64Decode(data.base64);
    var blob = Utilities.newBlob(fileContent, data.mimeType, data.filename);
    
    // Target Google Drive folder ID
    var folderId = "1BaEn7x30pS3TG2GOcjbBTil-oJldIt0x"; 
    var folder = DriveApp.getFolderById(folderId);
    
    // Create the file in the designated folder
    var file = folder.createFile(blob);
    
    return ContentService.createTextOutput(JSON.stringify({
      success: true,
      fileId: file.getId(),
      url: file.getUrl()
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
