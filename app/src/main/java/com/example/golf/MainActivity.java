package com.example.golf;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.MediaController;
import android.widget.Toast;
import android.widget.VideoView;
import com.amazonaws.auth.CognitoCachingCredentialsProvider;
import com.amazonaws.mobileconnectors.s3.transferutility.TransferObserver;
import com.amazonaws.mobileconnectors.s3.transferutility.TransferUtility;
import com.amazonaws.regions.Region;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3Client;
import java.io.File;


public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    private String TAG = "MainActivity";
    public static Context mContext;
    CognitoCachingCredentialsProvider credentialsProvider;
    AmazonS3 s3;
    TransferUtility transferUtility;

    Button sendBtn, retryBtn;
    ImageButton playBtn;
    VideoView Videoview;
    File f;
    private String userChoosenTask;
    Uri VideoUri;
    String videopath;
    private Uri mImageUri;
    private int PICTURE_CHOICE = 1;
    private int REQUEST_CAMERA = 2;
    private int SELECT_FILE = 3;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        mContext = this;
        sendBtn = (Button) findViewById(R.id.send);
        retryBtn = (Button) findViewById(R.id.retry);
        Videoview = (VideoView) findViewById(R.id.video_card);
        playBtn = (ImageButton) findViewById(R.id.Vidplay);
        sendBtn.setOnClickListener(this);
        retryBtn.setOnClickListener(this);

        credentialsProvider = new CognitoCachingCredentialsProvider(
                getApplicationContext(),
                "ap-northeast-2:8c1ea4a3-6b45-4d03-a486-d7459dda3815", // 자격 증명 풀 ID
                Regions.AP_NORTHEAST_2 // 리전
        );
        s3 = new AmazonS3Client(credentialsProvider);
        transferUtility = new TransferUtility(s3, getApplicationContext());
        s3.setRegion(Region.getRegion(Regions.AP_NORTHEAST_2));
        s3.setEndpoint("s3.ap-northeast-2.amazonaws.com");

        transferUtility = new TransferUtility(s3, getApplicationContext());


    }



    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.send:
                double bytes = f.length();
                double kilobytes = (bytes/1024);
                double megabytes = (kilobytes/1024);
                if(megabytes>1){
                    Toast.makeText(this.getApplicationContext(),"파일 용량이 너무 큽니다.", Toast.LENGTH_SHORT).show();
                }
                else {
                    TransferObserver observer = transferUtility.upload(
                            "golfapplication",
                            f.getName(),
                            f
                    );
                    break;
                }
            case R.id.retry:
                selectImage();
                break;
        }
    }

    private void selectImage() {

        Log.d(TAG, "select Image");
        final CharSequence[] items = {"촬영하기", "사진 가져오기",
                "취소"};

        AlertDialog.Builder builder1 = new AlertDialog.Builder(this);
        builder1.setTitle("사진가져오기");
        builder1.setItems(items, new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int item) {
                boolean result = Utility.checkPermission(getApplicationContext());

                if (items[item].equals("촬영하기")) {
                    userChoosenTask = "촬영하기";
                    if (result)
                        cameraIntent();


                } else if (items[item].equals("사진 가져오기")) {
                    userChoosenTask = "사진 가져오기";
                    if (result)
                        galleryIntent();

                } else if (items[item].equals("취소")) {
                    dialog.dismiss();
                }
            }
        });
        AlertDialog alertDialog2 = builder1.create();
        builder1.show();

    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        switch (requestCode) {
            case Utility.MY_PERMISSIONS_REQUEST_WRITE_EXTERNAL_STORAGE:
                if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    if (userChoosenTask.equals("촬영하기"))
                        cameraIntent();
                    else if (userChoosenTask.equals("사진 가져오기"))
                        galleryIntent();
                } else {
                    //code for deny
                }
                break;
        }
    }

    public void galleryIntent() {
        Log.d(TAG, "Gallery Intent");
        Intent intent = new Intent();
        intent.setType("video/*");
        intent.setAction(Intent.ACTION_GET_CONTENT);//
        startActivityForResult(Intent.createChooser(intent, "Select File"), SELECT_FILE);
    }

    private void cameraIntent() {
        startActivityForResult(new Intent(MainActivity.this,camera.class), REQUEST_CAMERA);
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (resultCode == Activity.RESULT_OK) {
            if (requestCode == SELECT_FILE) {
                Log.d(TAG, "onActivityResult, SELECT_FILE");
                onSelectFromGalleryResult(data, SELECT_FILE);
            }
            else if(requestCode == REQUEST_CAMERA)
            {
                galleryIntent();
            }
        }
    }

    private void onSelectFromGalleryResult(Intent data, int imagetype) {
        final MediaController mediaController =
                new MediaController(this);
        Log.d(TAG, "onSelectFromGalleryResult");
        VideoUri = data.getData();
        if (Build.VERSION.SDK_INT < 11) {
            videopath = RealPathUtil.getRealPathFromURI_BelowAPI11(this, VideoUri);
            Log.d(TAG, Build.VERSION.SDK_INT + "");
        } else if (Build.VERSION.SDK_INT < 19) {
            Log.d(TAG, Build.VERSION.SDK_INT + "");
            videopath = RealPathUtil.getRealPathFromURI_API11to18(this, VideoUri);
        } else {
            Log.d(TAG, Build.VERSION.SDK_INT + "");
            videopath = RealPathUtil.getRealPathFromURI_API19(this, VideoUri);
        }
        f = new File(videopath);
        Videoview.setVideoURI(VideoUri);
        playBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                Videoview.setMediaController(mediaController);

                Videoview.start();

            }
        });
    }
}